/* ============================================================
   Corralón 2 de Abril — catálogo digital + pedido por WhatsApp
   ============================================================ */
(function () {
  "use strict";
  const CFG = window.CONFIG || {};
  const DATA = window.CATALOG || { categories: [], products: [] };
  const PAGE = 48;

  // índices
  const CATS = DATA.categories;
  const CAT_BY = {}; CATS.forEach(c => CAT_BY[c.slug] = c);
  const PRODS = DATA.products;
  const PROD_BY = {}; PRODS.forEach(p => PROD_BY[p.id] = p);

  // estado
  const cart = new Map(loadCart());        // id -> qty
  let view = { mode: "home", slug: null, q: "" };
  let list = [];      // lista actual filtrada
  let shown = 0;

  // ---------- utilidades ----------
  const $ = s => document.querySelector(s);
  const el = (t, c, h) => { const e = document.createElement(t); if (c) e.className = c; if (h != null) e.innerHTML = h; return e; };
  const money = n => CFG.currency + " " + Math.round(n).toLocaleString("es-AR");
  const catImg = slug => `img/cat/${slug}.jpg`;
  const DISC = Number(CFG.webDiscount) || 0;
  const webPrice = p => Math.round(p * (1 - DISC / 100));
  // imagen por TIPO de producto con respaldo a la imagen de categoría
  const prodImgTag = (p, cls) =>
    `<img class="${cls || ""}" src="img/prod/${p.t || "_"}.webp" alt="" loading="lazy" onerror="this.onerror=null;this.src='${catImg(p.cat)}'"/>`;
  const norm = s => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

  function loadCart() { try { return JSON.parse(localStorage.getItem("c2a_cart") || "[]"); } catch { return []; } }
  function saveCart() { localStorage.setItem("c2a_cart", JSON.stringify([...cart])); }

  // ---------- branding estático ----------
  function fillStatic() {
    $("#heroTag").textContent = CFG.tagline + " · " + CFG.city;
    const chips = [
      CFG.rating ? `<span class="chip star">★ <b>${CFG.rating}</b> (${CFG.reviews}+)</span>` : "",
      CFG.delivery ? `<span class="chip">🚚 ${CFG.delivery}</span>` : "",
      CFG.hours ? `<span class="chip">🕒 ${CFG.hours}</span>` : "",
      CFG.address ? `<span class="chip">📍 ${CFG.address}</span>` : "",
    ].join("");
    $("#heroChips").innerHTML = chips;
    const waBase = `https://wa.me/${CFG.whatsapp}?text=${encodeURIComponent("¡Hola! Quería hacer una consulta sobre materiales.")}`;
    $("#heroWa").href = waBase;
    $("#ftrWa").href = waBase;
    $("#ftrAddr").textContent = "📍 " + CFG.address;
    $("#ftrHours").textContent = "🕒 " + CFG.hours;
    $("#ftrDelivery").textContent = "🚚 " + CFG.delivery;
    $("#yr").textContent = "2026";

    // cinta promo (marquesina)
    if (DISC > 0) {
      const cond = CFG.discountCondition || "pagando en efectivo al retirar";
      const m = `💵 <b>${DISC}% OFF</b> comprando por la web ${cond} <span class="sep">◆</span> 🚚 ${CFG.delivery} <span class="sep">◆</span> 🧱 Más de ${PRODS.length.toLocaleString("es-AR")} productos para tu obra <span class="sep">◆</span> 💵 <b>${DISC}% OFF</b> en efectivo al retirar <span class="sep">◆</span>`;
      $("#promoMarq").innerHTML = m + m;
      $("#heroPromo").innerHTML =
        `<span class="pct">${DISC}%</span>
         <span class="ptx">OFF comprando por la web<small>${cond} · armá tu pedido y retiralo</small></span>`;
    } else {
      $("#promoStrip").style.display = "none";
      $("#heroPromo").style.display = "none";
    }
  }

  // ---------- routing ----------
  function go(mode, slug) {
    view = { mode, slug: slug || null, q: view.q };
    if (mode !== "search") $("#q").value = "", view.q = "";
    try { history.replaceState(null, "", mode === "category" && slug ? "#cat=" + slug : "#"); } catch (e) {}
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
    render();
  }

  function computeList() {
    if (view.mode === "search") {
      const terms = norm(view.q).split(/\s+/).filter(Boolean);
      list = PRODS.filter(p => { const n = norm(p.name + " " + (p.brand || "")); return terms.every(t => n.includes(t)); });
    } else if (view.mode === "category") {
      list = PRODS.filter(p => p.cat === view.slug);
    } else {
      list = [];
    }
  }

  // ---------- render principal ----------
  function render() {
    const vw = $("#view"), head = $("#secHead"), more = $("#moreBtn");
    vw.innerHTML = ""; head.innerHTML = ""; shown = 0; more.hidden = true;
    $("#hero").style.display = view.mode === "home" ? "" : "none";

    if (view.mode === "home") { renderHome(vw); return; }

    computeList();
    // encabezado de sección
    const title = view.mode === "search"
      ? `Resultados para “${view.q}”`
      : (CAT_BY[view.slug] ? CAT_BY[view.slug].name : "Productos");
    head.appendChild(el("button", "back-btn", "← Volver"));
    head.querySelector(".back-btn").onclick = () => go("home");
    head.appendChild(el("h2", null, title));
    head.appendChild(el("span", "count", `${list.length} producto${list.length === 1 ? "" : "s"}`));

    if (!list.length) {
      vw.appendChild(el("div", "empty", `<h3>Sin resultados</h3><p>Probá con otra palabra o mirá las categorías.</p>`));
      return;
    }
    const grid = el("div", "prod-grid"); vw.appendChild(grid);
    grid.id = "grid";
    appendPage(grid);
  }

  function renderHome(vw) {
    // categorías
    const h = el("div", "section-head"); h.style.padding = "26px 0 4px";
    h.appendChild(el("h2", null, "Rubros"));
    h.appendChild(el("span", "count", `${PRODS.length.toLocaleString("es-AR")} productos en ${CATS.length} categorías`));
    const wrap = el("div", "wrap"); wrap.appendChild(h);
    const grid = el("div", "cat-grid");
    CATS.forEach(c => {
      const card = el("a", "cat-card");
      card.href = "javascript:void 0";
      card.innerHTML =
        `<img src="${catImg(c.slug)}" alt="${c.name}" loading="lazy"/>
         <div class="cat-ov"></div>
         <span class="cat-tag">${c.count}</span>
         <div class="cat-tx"><h3>${c.name}</h3><span>Ver productos →</span></div>`;
      card.onclick = () => go("category", c.slug);
      grid.appendChild(card);
    });
    wrap.appendChild(grid);
    vw.appendChild(wrap);
  }

  function appendPage(grid) {
    const slice = list.slice(shown, shown + PAGE);
    slice.forEach(p => grid.appendChild(card(p)));
    shown += slice.length;
    $("#moreBtn").hidden = shown >= list.length;
  }

  // ---------- tarjeta de producto ----------
  function card(p) {
    const c = el("div", "card");
    const wp = webPrice(p.price);
    const prices = DISC > 0
      ? `<div class="card-prices">
           <span class="card-list">${money(p.price)}</span>
           <span class="card-web"><span class="lbl">💵 precio web efectivo</span>${money(wp)}</span>
         </div>`
      : `<div class="card-prices"><span class="card-web">${money(p.price)}</span></div>`;
    c.innerHTML =
      `<div class="card-img">${prodImgTag(p)}
        <span class="card-cat">${CAT_BY[p.cat] ? CAT_BY[p.cat].name : ""}</span>
        ${DISC > 0 ? `<span class="card-off">-${DISC}%</span>` : ""}</div>
       <div class="card-bd">
         <div class="card-name">${p.name}</div>
         ${p.brand ? `<div class="card-brand">${p.brand}</div>` : ""}
         <div class="card-foot">
           ${prices}
           <div class="ctrl"></div>
         </div>
       </div>`;
    renderCtrl(c.querySelector(".ctrl"), p);
    return c;
  }

  function renderCtrl(box, p) {
    box.__pid = p.id;
    const qty = cart.get(p.id) || 0;
    box.innerHTML = "";
    if (qty === 0) {
      const b = el("button", "add-btn", "Agregar");
      b.onclick = () => { setQty(p.id, 1); flash(p); };
      box.appendChild(b);
    } else {
      const s = el("div", "stepper");
      s.innerHTML = `<button>−</button><span>${qty}</span><button>+</button>`;
      const [minus, , plus] = s.children;
      minus.onclick = () => setQty(p.id, qty - 1);
      plus.onclick = () => setQty(p.id, qty + 1);
      box.appendChild(s);
    }
  }

  function setQty(id, q) {
    if (q <= 0) cart.delete(id); else cart.set(id, q);
    saveCart(); syncBadge(); syncControls(id); renderCart();
  }

  // re-renderiza los controles visibles del producto modificado (toda la grilla)
  function syncControls(id) {
    const grid = $("#grid");
    if (!grid) return;
    grid.querySelectorAll(".ctrl").forEach(ctrl => {
      if (ctrl.__pid === id) renderCtrl(ctrl, PROD_BY[id]);
    });
  }

  function flash(p) { toast(`Agregado: ${p.name.slice(0, 28)}${p.name.length > 28 ? "…" : ""}`); }

  // ---------- badge / toast ----------
  function syncBadge() {
    let n = 0; cart.forEach(q => n += q);
    const b = $("#cartBadge"); b.textContent = n; b.hidden = n === 0;
  }
  let toastT;
  function toast(msg) {
    let t = $("#toast"); if (!t) { t = el("div", "toast"); t.id = "toast"; document.body.appendChild(t); }
    t.textContent = msg; requestAnimationFrame(() => t.classList.add("show"));
    clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 1800);
  }

  // ---------- carrito ----------
  function cartTotals() {
    let subtotal = 0;
    cart.forEach((q, id) => { const p = PROD_BY[id]; if (p) subtotal += p.price * q; });
    const web = Math.round(subtotal * (1 - DISC / 100));
    return { subtotal, web, save: subtotal - web };
  }

  function renderCart() {
    const body = $("#cartList"); body.innerHTML = "";
    if (cart.size === 0) {
      body.appendChild(el("div", "cart-empty", "<h3>🛒</h3><p>Tu pedido está vacío.<br>Agregá materiales del catálogo.</p>"));
      $("#cartSubtotal").textContent = money(0);
      $("#cartTotal").textContent = money(0);
      $("#cartDiscount").textContent = "-" + money(0);
      $("#cartSave").textContent = "";
      $("#cartDiscLine").style.display = DISC > 0 ? "" : "none";
      $("#waCheckout").disabled = true;
      return;
    }
    cart.forEach((q, id) => {
      const p = PROD_BY[id]; if (!p) return;
      const ci = el("div", "ci");
      ci.innerHTML =
        `${prodImgTag(p)}
         <div class="ci-bd">
           <div class="ci-name">${p.name}</div>
           <div class="ci-row">
             <div class="ci-stepper"><button>−</button><span>${q}</span><button>+</button></div>
             <div class="ci-price">${money(webPrice(p.price) * q)}</div>
           </div>
           <button class="ci-rm">Quitar</button>
         </div>`;
      const st = ci.querySelector(".ci-stepper");
      st.children[0].onclick = () => setQty(id, q - 1);
      st.children[2].onclick = () => setQty(id, q + 1);
      ci.querySelector(".ci-rm").onclick = () => setQty(id, 0);
      body.appendChild(ci);
    });
    const t = cartTotals();
    $("#cartSubtotal").textContent = money(t.subtotal);
    $("#cartDiscLabel").textContent = `Descuento web (${DISC}%)`;
    $("#cartDiscount").textContent = "- " + money(t.save);
    $("#cartDiscLine").style.display = DISC > 0 ? "" : "none";
    $("#cartTotal").textContent = money(t.web);
    $("#cartSave").innerHTML = DISC > 0
      ? `🎉 Ahorrás <b>${money(t.save)}</b> ${CFG.discountCondition || "pagando en efectivo al retirar"}`
      : "";
    $("#waCheckout").disabled = false;
  }

  function checkout() {
    if (cart.size === 0) return;
    let lines = [`*PEDIDO WEB — ${CFG.name}*`, ""], i = 0;
    cart.forEach((q, id) => {
      const p = PROD_BY[id]; if (!p) return;
      i++;
      lines.push(`${i}) ${p.name}`);
      lines.push(`    ${q} x ${money(webPrice(p.price))} = ${money(webPrice(p.price) * q)}`);
    });
    const t = cartTotals();
    lines.push("", "————————————————");
    if (DISC > 0) {
      lines.push(`Subtotal lista: ${money(t.subtotal)}`,
        `Descuento web ${DISC}%: -${money(t.save)}`,
        `*TOTAL WEB EFECTIVO: ${money(t.web)}*`,
        `_(${DISC}% OFF ${CFG.discountCondition || "pagando en efectivo al retirar"} · no incluye flete)_`);
    } else {
      lines.push(`*TOTAL: ${money(t.web)}*`, "_(no incluye flete · sujeto a confirmación)_");
    }
    lines.push("", "Mi nombre: ", "¿Retiro o envío?: ", "Dirección (si es envío): ");
    const url = `https://wa.me/${CFG.whatsapp}?text=${encodeURIComponent(lines.join("\n"))}`;
    window.open(url, "_blank");
  }

  // ---------- drawer ----------
  function openCart(o) {
    $("#drawer").classList.toggle("open", o);
    $("#drawer").setAttribute("aria-hidden", o ? "false" : "true");
    $("#drawerBg").hidden = !o;
    if (o) renderCart();
  }

  // ---------- búsqueda ----------
  let searchT;
  function onSearch(v) {
    $("#qClear").hidden = !v;
    clearTimeout(searchT);
    searchT = setTimeout(() => {
      view.q = v.trim();
      if (view.q.length === 0) { go("home"); return; }
      view.mode = "search"; render();
    }, 180);
  }

  // ---------- init ----------
  function init() {
    fillStatic(); syncBadge();
    $("#q").addEventListener("input", e => onSearch(e.target.value));
    $("#qClear").onclick = () => { $("#q").value = ""; onSearch(""); $("#q").focus(); };
    $("#cartBtn").onclick = () => openCart(true);
    $("#drawerClose").onclick = () => openCart(false);
    $("#drawerBg").onclick = () => openCart(false);
    $("#waCheckout").onclick = checkout;
    $("#homeLink").onclick = e => { e.preventDefault(); go("home"); };
    $("#moreBtn").onclick = () => { const g = $("#grid"); if (g) appendPage(g); };
    document.addEventListener("keydown", e => { if (e.key === "Escape") openCart(false); });
    const m = (location.hash || "").match(/cat=([\w-]+)/);
    if (m && CAT_BY[m[1]]) go("category", m[1]); else render();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
