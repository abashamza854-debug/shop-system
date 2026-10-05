from flask import Flask, request, redirect, render_template_string, session, jsonify, jsonify
import sqlite3
import os
import uuid

app = Flask(__name__)

# =========================
# الإعدادات
# =========================

DB = "shop.db"
UPLOAD_FOLDER = "static/uploads"

# غيّرها إلى كلمة سر خاصة بك
ADMIN_PASSWORD = "10002000"

# مهم للجلسات
app.secret_key = "change-this-secret-key"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# =========================
# قاعدة البيانات
# =========================

def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            size TEXT,
            color TEXT,
            image TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# تصميم المتجر
# =========================

SHOP_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>متجر الملابس</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial;
    background: #f4f4f5;
}

header {
    background: #111827;
    color: white;
    padding: 30px 20px;
    text-align: center;
}

.container {
    max-width: 1100px;
    margin: auto;
    padding: 20px;
}

.products {
    display: grid;
    grid-template-columns:
    repeat(auto-fit, minmax(220px, 1fr));
    gap: 18px;
}

.product {
    background: white;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 3px 12px #0001;
}

.product img {
    width: 100%;
    height: 280px;
    object-fit: cover;
}

.info {
    padding: 15px;
}

.price {
    font-size: 21px;
    font-weight: bold;
}

.buy {
    width: 100%;
    padding: 13px;
    border: 0;
    border-radius: 10px;
    background: #111827;
    color: white;
    font-size: 16px;
}
.cart-button {
    display: inline-block;
    margin-top: 15px;
    padding: 12px 25px;
    background: #ffffff;
    color: #222;
    text-decoration: none;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
}

.cart-button:hover {
    opacity: 0.9;
}
</style>

</head>

<body>



<header>
    <h1>👕 متجر الملابس</h1>

    <p>أحدث المنتجات</p>

    <a href="/cart" class="cart-button">
        🛒 السلة
    </a>

</header>

<div class="container">

<h2>🛍️ المنتجات</h2>

<div style="margin:15px 0;">
<input id="productSearch" type="text"
placeholder="🔎 ابحث عن اسم المنتج..."
oninput="filterProducts()"
style="width:100%; padding:14px; border:1px solid #ddd; border-radius:12px; font-size:16px; box-sizing:border-box;">

<div style="display:flex; gap:8px; flex-wrap:wrap; margin-top:10px;">
<button type="button" onclick="filterCategory('الكل')">الكل</button>
<button type="button" onclick="filterCategory('قمصان')">👕 قمصان</button>
<button type="button" onclick="filterCategory('بناطيل')">👖 بناطيل</button>
<button type="button" onclick="filterCategory('أحذية')">👟 أحذية</button>
<button type="button" onclick="filterCategory('جاكيتات')">🧥 جاكيتات</button>
<button type="button" onclick="filterCategory('إكسسوارات')">🧢 إكسسوارات</button>
</div>
</div>

<div class="products">

{% for p in products %}

<div class="product" data-name="{{ p[1] }}" data-category="{{ p[8] }}">

<div style="display:flex; gap:8px; flex-wrap:wrap; justify-content:center;">

{% if p[5] %}
<img src="/static/uploads/{{ p[5] }}"
style="width:100%; max-width:100%; border-radius:12px;">
{% endif %}

{% if p[6] %}
<img src="/static/uploads/{{ p[6] }}"
style="width:31%; border-radius:10px;">
{% endif %}

{% if p[7] %}
<img src="/static/uploads/{{ p[7] }}"
style="width:31%; border-radius:10px;">
{% endif %}

</div>

<div class="info">

<h3>{{ p[1] }}</h3>

<p class="price">
{{ p[2] }} د.ع
</p>
<form method="POST" action="/add-to-cart/{{ p[0] }}"> 

{% if p[3] %}
<div style="margin:10px 0;">
<strong>📏 اختر المقاسات:</strong>
<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;">
{% for size in p[3].split(",") %}
<label style="border:1px solid #ddd;padding:8px 12px;border-radius:8px;">
<input type="checkbox" name="sizes" value="{{ size.strip() }}"> {{ size.strip() }}
</label>
{% endfor %}
</div>
</div>
{% endif %}

{% if p[4] %}
<div style="margin:10px 0;">
<strong>🎨 اختر الألوان:</strong>
<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:8px;">
{% for color in p[4].split(",") %}
<label style="border:1px solid #ddd;padding:8px 12px;border-radius:8px;">
<input type="checkbox" name="colors" value="{{ color.strip() }}"> {{ color.strip() }}
</label>
{% endfor %}
</div>
</div>
{% endif %}

🛒 شراء
<button type="submit"
style="
display:block;
width:100%;
padding:13px;
border-radius:10px;
background:#111827;
color:white;
text-align:center;
border:none;
font-size:16px;
cursor:pointer;
">
🛒 أضف للسلة
</button>
</form>

</div>

</div>

{% else %}

<p>ماكو منتجات حاليًا.</p>

{% endfor %}

</div>

</div>

<script>
function openMap(lat, lon) {
    const url = "geo:" + lat + "," + lon + "?q=" + lat + "," + lon;
    window.location.href = url;
}
</script>


<script>
let selectedCategory = "الكل";

function filterCategory(category) {
    selectedCategory = category;
    filterProducts();
}

function filterProducts() {
    const search = document.getElementById("productSearch").value.toLowerCase().trim();
    const products = document.querySelectorAll(".product");

    products.forEach(function(product) {
        const name = (product.dataset.name || "").toLowerCase();
        const category = product.dataset.category || "";

        const matchesSearch = name.includes(search);
        const matchesCategory =
            selectedCategory === "الكل" ||
            category === selectedCategory;

        product.style.display =
            matchesSearch && matchesCategory ? "" : "none";
    });
}
</script>

</body>
</html>
"""


# =========================
# تسجيل دخول الأدمن
# =========================

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>دخول الإدارة</title>

<style>

body {
    margin: 0;
    background: #f4f4f5;
    font-family: Arial;
}

.box {
    max-width: 400px;
    margin: 80px auto;
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 3px 15px #0002;
}

input {
    width: 100%;
    padding: 14px;
    margin: 10px 0;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 16px;
}

button {
    width: 100%;
    padding: 14px;
    border: 0;
    border-radius: 10px;
    background: #111827;
    color: white;
    font-size: 16px;
}

.error {
    color: #dc2626;
}

</style>

</head>

<body>

<div class="box">

<h2>🔐 لوحة الإدارة</h2>

{% if error %}

<p class="error">
❌ كلمة السر غير صحيحة
</p>

{% endif %}

<form method="POST">

<input
type="password"
name="password"
placeholder="كلمة السر"

<button type="submit">
دخول
</button>

</form>

</div>

</body>
</html>
"""


# =========================
# لوحة التحكم
# =========================

ADMIN_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>لوحة التحكم</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #f4f4f5;
    font-family: Arial;
}

header {
    background: #111827;
    color: white;
    padding: 20px;
}

.container {
    max-width: 1000px;
    margin: auto;
    padding: 20px;
}

.box {
    background: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
}

.stat {
    background: white;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    border: 1px solid #e5e7eb;
}

.stat-icon {
    font-size: 32px;
    margin-bottom: 8px;
}

.stat-number {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 5px;
}

.stat-title {
    color: #6b7280;
    font-size: 15px;
}

input {
    width: 100%;
    padding: 13px;
    margin: 6px 0;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 16px;
}

button {
    width: 100%;
    padding: 13px;
    border: 0;
    border-radius: 10px;
    background: #111827;
    color: white;
    font-size: 16px;
}

.delete {
    background: #dc2626;
}

.logout {
    background: #6b7280;
}

.products {
    display: grid;
    grid-template-columns:
    repeat(auto-fit, minmax(220px, 1fr));
    gap: 15px;
}

.product {
    background: #f9fafb;
    border-radius: 12px;
    overflow: hidden;
}

.product img {
    width: 100%;
    height: 220px;
    object-fit: cover;
}

.info {
    padding: 15px;
}

.price {
    font-size: 20px;
    font-weight: bold;
}

.order {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 15px;
}

.order h3 {
    margin-top: 0;
}

.order-item {
    background: white;
    padding: 12px;
    margin: 8px 0;
    border-radius: 10px;
    display: flex;
    justify-content: space-between;
    gap: 10px;
    border: 1px solid #eee;
}

.order-total {
    margin-top: 12px;
    padding: 12px;
    background: #111827;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}

select {
    width: 100%;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 16px;
    background: white;
}

</style>

</head>

<body>

<header>

<h1>⚙️ لوحة التحكم</h1>

</header>

<div class="container">

<div class="stats">

<div class="stat">
<div class="stat-icon">👕</div>
<div class="stat-number">{{ product_count }}</div>
<div class="stat-title">المنتجات</div>
</div>

<div class="stat">
<div class="stat-icon">📦</div>
<div class="stat-number">{{ order_count }}</div>
<div class="stat-title">كل الطلبات</div>
</div>

<div class="stat">
<div class="stat-icon">🆕</div>
<div class="stat-number">{{ new_orders }}</div>
<div class="stat-title">طلبات جديدة</div>
</div>

<div class="stat">
<div class="stat-icon">💰</div>
<div class="stat-number">{{ total_sales }} د.ع</div>
<div class="stat-title">المبيعات</div>
</div>

</div>

<div class="box">

<h2>➕ إضافة منتج</h2>

<form
method="POST"
action="/add"
enctype="multipart/form-data">

<input
name="name"
placeholder="اسم القطعة"
required>

<input
name="price"
type="number"
step="0.01"
placeholder="السعر بالدينار"
required>

<label>📏 المقاسات المتوفرة</label>

<div style="display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 15px;">
  <label><input type="checkbox" name="sizes" value="S"> S</label>
  <label><input type="checkbox" name="sizes" value="M"> M</label>
  <label><input type="checkbox" name="sizes" value="L"> L</label>
  <label><input type="checkbox" name="sizes" value="XL"> XL</label>
  <label><input type="checkbox" name="sizes" value="XXL"> XXL</label>
</div>

<label>🎨 الألوان المتوفرة</label>

<div style="display:flex; flex-wrap:wrap; gap:8px; margin:8px 0 15px;">
  <label><input type="checkbox" name="colors" value="أبيض"> أبيض</label>
  <label><input type="checkbox" name="colors" value="أسود"> أسود</label>
  <label><input type="checkbox" name="colors" value="أحمر"> أحمر</label>
  <label><input type="checkbox" name="colors" value="أزرق"> أزرق</label>
  <label><input type="checkbox" name="colors" value="أخضر"> أخضر</label>
  <label><input type="checkbox" name="colors" value="أصفر"> أصفر</label>
</div>

<select name="category" required>
  <option value="قمصان">👕 قمصان</option>
  <option value="بناطيل">👖 بناطيل</option>
  <option value="أحذية">👟 أحذية</option>
  <option value="جاكيتات">🧥 جاكيتات</option>
  <option value="إكسسوارات">🧢 إكسسوارات</option>
  <option value="أخرى">📦 أخرى</option>
</select>

<input
  name="image"
type="file"
accept="image/*"
required>

<input
name="image2"
type="file"
accept="image/*">

<input
name="image3"
type="file"
accept="image/*">

<button type="submit">
➕ إضافة المنتج
</button>

</form>

</div>


<div class="box">

<h2>🛍️ المنتجات</h2>

<div class="products">

{% for p in products %}

<div class="product">

{% if p[5] %}

<img src="/static/uploads/{{ p[5] }}">

{% endif %}

<div class="info">

<h3>{{ p[1] }}</h3>

<p class="price">
{{ p[2] }} د.ع
</p>

<p>
📏 {{ p[3] or "غير محدد" }}
</p>

<p>
🎨 {{ p[4] or "غير محدد" }}
</p>

<form
method="POST"
action="/delete/{{ p[0] }}">

<button class="delete">
🗑️ حذف
</button>

</form>

</div>

</div>

{% endfor %}

</div>

</div>


<div class="box">

<h2>📦 الطلبات</h2>

{% if orders %}
    {% for o in orders %}
    <div class="order">

        <h3>🧾 طلب رقم #{{ o[0] }}</h3>

        <a href="/order/{{ o[0] }}"
           style="
           display:block;
           text-align:center;
           padding:12px;
           margin-bottom:15px;
           background:#2563eb;
           color:white;
           text-decoration:none;
           border-radius:10px;">
            👁️ عرض تفاصيل الطلب
        </a>

        <p>👤 <b>الاسم:</b> {{ o[1] }}</p>
        <p>📞 <b>الهاتف:</b> {{ o[2] }}</p>
        <p>📍 <b>العنوان:</b> {{ o[3] }}</p>

          {% if o[11] is not none and o[12] is not none %}

<div style="margin:12px 0;">

    <div id="map-{{ o[0] }}"
         style="width:100%; height:280px; border-radius:12px; overflow:hidden;">
    </div>

    <button type="button"
            onclick="window.location.href='waze://?ll={{ o[10] }},{{ o[11] }}&navigate=yes'"
            style="display:block; width:100%; padding:12px; margin-top:10px; background:#16a34a; color:white; border:none; border-radius:10px; font-size:16px;">
        📍 فتح الطريق في Waze
    </button>

    <p id="route-info-{{ o[0] }}"
       style="text-align:center; margin:8px 0; color:#555;">
    </p>

</div>

{% else %}
<p style="color:#888;">📍 لم يتم تحديد موقع على الخريطة</p>
{% endif %}
        <p>🕐 <b>التاريخ:</b> {{ o[9] }}</p>

        <h4>🛍️ المنتجات:</h4>

        {% if order_items.get(o[0]) %}
            {% for item in order_items[o[0]] %}
            <div class="order-item">
                <div>
                    <b>👕 {{ item[0] }}</b>
                    <br>
                    🔢 الكمية: {{ item[1] }}
                      📏 المقاسات: {{ item[4] or "غير محدد" }}<br>
                      🎨 الألوان: {{ item[5] or "غير محدد" }}

                </div>

                <div>
                    {{ item[3] }} د.ع
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="order-item">
                <b>{{ o[4] }}</b>
                <span>الكمية: {{ o[5] }}</span>
            </div>
        {% endif %}

        <div class="order-total">
            💵 المجموع الكلي: {{ o[7] }} د.ع
        </div>

        <form method="POST" action="/update_order/{{ o[0] }}">
            <label><b>حالة الطلب:</b></label>

            <select name="status">
                <option value="جديد" {% if o[8] == "جديد" %}selected{% endif %}>🆕 جديد</option>
                <option value="قيد التجهيز" {% if o[8] == "قيد التجهيز" %}selected{% endif %}>📦 قيد التجهيز</option>
                <option value="تم التسليم" {% if o[8] == "تم التسليم" %}selected{% endif %}>✅ تم التسليم</option>
                <option value="ملغي" {% if o[8] == "ملغي" %}selected{% endif %}>❌ ملغي</option>
            </select>

            <button type="submit">تحديث الحالة</button>
        </form>

        <form method="POST"
              action="/delete_order/{{ o[0] }}"
              onsubmit="return confirm('هل أنت متأكد من حذف هذا الطلب؟');"
              style="margin-top:10px;">

            <button type="submit" class="delete">
                🗑️ حذف الطلب
            </button>

        </form>

    </div>
    {% endfor %}
{% else %}
    <p>📭 لا توجد طلبات حتى الآن.</p>
{% endif %}

<form action="/logout">

<button class="logout">
🚪 تسجيل خروج
</button>

</form>

</div>

</div>


<script>
function openWaze(lat, lon) {
    const intentUrl =
        "intent://?ll=" + encodeURIComponent(lat + "," + lon) +
        "&navigate=yes#Intent;scheme=waze;package=com.waze;action=android.intent.action.VIEW;end";

    window.location.href = intentUrl;
}
</script>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const orderMaps = {};

function initOrderMap(id, lat, lon) {

    try {

        const element =
            document.getElementById("map-" + id);

        if (!element) {
            console.error(
                "Map element not found:",
                "map-" + id
            );
            return;
        }

        const latitude = Number(lat);
        const longitude = Number(lon);

        if (
            !Number.isFinite(latitude) ||
            !Number.isFinite(longitude)
        ) {
            console.error(
                "Invalid coordinates:",
                lat,
                lon
            );
            return;
        }

        const map =
            L.map(element, {
                zoomControl: true
            }).setView(
                [latitude, longitude],
                15
            );

        L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
            {
                maxZoom: 19,
                attribution:
                    "Tiles &copy; Esri"
            }
        ).addTo(map);

        const marker =
            L.marker([
                latitude,
                longitude
            ]).addTo(map);

        marker
            .bindPopup("📍 موقع الزبون")
            .openPopup();

        orderMaps[String(id)] = map;

        orderMaps[String(id)].customerMarker =
            marker;

        setTimeout(function() {
            map.invalidateSize(true);
        }, 500);

        console.log(
            "Map ready:",
            id
        );

    } catch (error) {

        console.error(
            "Map initialization error:",
            error
        );

        const info =
            document.getElementById(
                "route-info-" + id
            );

        if (info) {
            info.textContent =
                "❌ تعذر تشغيل الخريطة";
        }
    }
}

function startWalking(id, destLat, destLon) {

    id = String(id);

    let info = document.getElementById("route-info-" + id);

    if (!info) {
        return;
    }

    let map = orderMaps[id];

    /*
     * إذا لم تكن الخريطة مهيأة، نشغلها الآن
     */
    if (!map) {

        info.textContent = "🗺️ جاري تشغيل الخريطة...";

        try {
            initOrderMap(id, destLat, destLon);
            map = orderMaps[id];
        } catch (e) {
            console.error(e);
        }
    }

    if (!map) {
        info.textContent = "❌ تعذر تشغيل الخريطة";
        return;
    }

    if (!navigator.geolocation) {
        info.textContent =
            "❌ تحديد الموقع غير مدعوم في هذا المتصفح";
        return;
    }

    info.textContent = "📍 جاري تحديد موقعك...";

    navigator.geolocation.watchPosition(

        function(position) {

            const myLat =
                position.coords.latitude;

            const myLon =
                position.coords.longitude;

            info.textContent =
                "🚶 جاري حساب طريق المشي...";

            if (map.myMarker) {
                map.removeLayer(map.myMarker);
            }

            map.myMarker =
                L.marker([
                    myLat,
                    myLon
                ]).addTo(map);

            map.myMarker
                .bindPopup("📍 موقعك الحالي")
                .openPopup();

            const request = {

                locations: [
                    {
                        lat: myLat,
                        lon: myLon,
                        type: "break"
                    },
                    {
                        lat: Number(destLat),
                        lon: Number(destLon),
                        type: "break"
                    }
                ],

                costing: "pedestrian",

                directions_options: {
                    units: "kilometers"
                }
            };

            fetch(
                "/walking-route",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        my_lat: myLat,
                        my_lon: myLon,
                        dest_lat: Number(destLat),
                        dest_lon: Number(destLon)
                    })
                }
            )

            .then(function(response) {

                if (!response.ok) {
                    throw new Error(
                        "HTTP " + response.status
                    );
                }

                return response.json();
            })

            .then(function(data) {

                if (
                    !data.trip ||
                    !data.trip.legs ||
                    !data.trip.legs.length
                ) {
                    throw new Error(
                        "لا يوجد طريق"
                    );
                }

                const shape =
                    data.trip.legs[0].shape;

                const points =
                    decodePolyline6(shape);

                if (map.routeLayer) {
                    map.removeLayer(
                        map.routeLayer
                    );
                }

                map.routeLayer =
                    L.polyline(
                        points,
                        {
                            weight: 6,
                            opacity: 0.9
                        }
                    ).addTo(map);

                const layers = [
                    map.myMarker
                ];

                if (map.customerMarker) {
                    layers.push(
                        map.customerMarker
                    );
                }

                layers.push(
                    map.routeLayer
                );

                const group =
                    L.featureGroup(layers);

                map.fitBounds(
                    group.getBounds(),
                    {
                        padding: [30, 30]
                    }
                );

                const distance =
                    Number(
                        data.trip.summary.length
                    ).toFixed(2);

                const minutes =
                    Math.round(
                        Number(
                            data.trip.summary.time
                        ) / 60
                    );

                info.textContent =
                    "🚶 المسافة: " +
                    distance +
                    " كم — الوقت التقريبي: " +
                    minutes +
                    " دقيقة";
            })

            .catch(function(error) {

                console.error(
                    "Walking route error:",
                    error
                );

                info.textContent =
                    "❌ تعذر حساب طريق المشي: " +
                    (error.message || "خطأ غير معروف");
            });
        },

        function(error) {

            console.error(
                "Location error:",
                error
            );

            if (error.code === 1) {

                info.textContent =
                    "❌ اسمح للموقع حتى نحدد طريقك إلى الزبون";

            } else {

                info.textContent =
                    "❌ تعذر تحديد موقعك";
            }
        },

        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }
    );
}

function decodePolyline6(str) {

    let index = 0;

    let lat = 0;
    let lon = 0;

    const coordinates = [];

    while (index < str.length) {

        let result = 0;
        let shift = 0;
        let byte;

        do {

            byte =
                str.charCodeAt(index++) - 63;

            result |=
                (byte & 0x1f) << shift;

            shift += 5;

        } while (byte >= 0x20);

        const deltaLat =
            (result & 1)
                ? ~(result >> 1)
                : (result >> 1);

        lat += deltaLat;

        result = 0;
        shift = 0;

        do {

            byte =
                str.charCodeAt(index++) - 63;

            result |=
                (byte & 0x1f) << shift;

            shift += 5;

        } while (byte >= 0x20);

        const deltaLon =
            (result & 1)
                ? ~(result >> 1)
                : (result >> 1);

        lon += deltaLon;

        coordinates.push([
            lat / 1000000,
            lon / 1000000
        ]);
    }

    return coordinates;
}

document.addEventListener("DOMContentLoaded", function() {

    {% for o in orders %}
    {% if o[11] is not none and o[12] is not none %}
    initOrderMap(
        "{{ o[0] }}",
        {{ o[11] }},
        {{ o[12] }}
    );
    {% endif %}
    {% endfor %}

});
</script>

</body>

</html>
"""


# =========================
# حماية الأدمن
# =========================

def admin_required():

    return session.get("admin") is True


# =========================
# متجر الزبون
# =========================
def get_session_id():
    if "cart_session" not in session:
        session["cart_session"] = str(uuid.uuid4())

    return session["cart_session"]
@app.route('/walking-route', methods=['POST'])
def walking_route():

    try:
        import json
        import urllib.request

        data = request.get_json(force=True)
        print("ROUTE DATA:", data, flush=True)

        my_lat = float(data["my_lat"])
        my_lon = float(data["my_lon"])
        dest_lat = float(data["dest_lat"])
        dest_lon = float(data["dest_lon"])

        payload = {
            "locations": [
                {
                    "lat": my_lat,
                    "lon": my_lon,
                    "type": "break"
                },
                {
                    "lat": dest_lat,
                    "lon": dest_lon,
                    "type": "break"
                }
            ],
            "max_distance": 500000,
            "costing": "pedestrian",
            "directions_options": {
                "units": "kilometers"
            }
        }

        body = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            "https://valhalla1.openstreetmap.de/route",
            data=body,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "ClothingShop/1.0"
            },
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=30) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        return jsonify(result)

    except Exception as e:
        if hasattr(e, "read"):
            try:
                print("API ERROR BODY:", e.read().decode("utf-8"), flush=True)
            except Exception:
                pass

        print("Walking route error:", repr(e)); import traceback; traceback.print_exc()

        return jsonify({
            "error": str(e)
        }), 500


@app.route("/")
def home():

    conn = sqlite3.connect(DB)

    products = conn.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    conn.close()

    return render_template_string(
        SHOP_HTML,
        products=products
    )



# =========================
# نظام السلة
# =========================

@app.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):

    session_id = get_session_id()

    selected_sizes = ", ".join(request.form.getlist("sizes"))
    selected_colors = ", ".join(request.form.getlist("colors"))

    conn = sqlite3.connect(DB)

    product = conn.execute(
        "SELECT id FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return redirect("/")

    item = conn.execute(
        "SELECT id, quantity FROM cart_items WHERE session_id = ? AND product_id = ?",
        (session_id, product_id)
    ).fetchone()

    if item:
        conn.execute(
            "UPDATE cart_items SET quantity = quantity + 1, selected_sizes = ?, selected_colors = ? WHERE id = ?",
            (selected_sizes, selected_colors, item[0],)
        )
    else:
        conn.execute(
            "INSERT INTO cart_items (session_id, product_id, quantity, selected_sizes, selected_colors) VALUES (?, ?, 1, ?, ?)",
            (session_id, product_id, selected_sizes, selected_colors)
        )

    conn.commit()
    conn.close()

    return redirect("/cart")


@app.route("/cart")
def cart():

    session_id = get_session_id()

    conn = sqlite3.connect(DB)

    items = conn.execute("""
        SELECT
            cart_items.id,
            products.name,
            products.price,
            products.image,
            cart_items.quantity,
            cart_items.selected_sizes,
            cart_items.selected_colors,
            products.id
        FROM cart_items
        JOIN products ON products.id = cart_items.product_id
        WHERE cart_items.session_id = ?
        ORDER BY cart_items.id DESC
    """, (session_id,)).fetchall()

    conn.close()

    total = sum(item[2] * item[4] for item in items)

    return render_template_string("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>السلة</title>
<style>
body{
    font-family:Arial;
    background:#f5f5f5;
    margin:0;
    padding:20px;
}
.container{
    max-width:700px;
    margin:auto;
}
.item{
    background:white;
    padding:15px;
    margin-bottom:12px;
    border-radius:14px;
    display:flex;
    gap:15px;
    align-items:center;
}
.item img{
    width:80px;
    height:80px;
    object-fit:cover;
    border-radius:10px;
}
.info{
    flex:1;
}
.qty{
    display:flex;
    align-items:center;
    gap:8px;
    margin-top:8px;
}
button{
    border:0;
    border-radius:8px;
    padding:8px 13px;
    cursor:pointer;
}
.update{
    background:#111827;
    color:white;
}
.delete{
    background:#dc2626;
    color:white;
}
.total{
    background:white;
    padding:20px;
    border-radius:14px;
    font-size:20px;
    font-weight:bold;
    margin-top:15px;
}
.empty{
    text-align:center;
    background:white;
    padding:40px;
    border-radius:15px;
}
.back{
    display:block;
    text-align:center;
    margin-top:15px;
    text-decoration:none;
    color:#111827;
}
</style>
</head>
<body>

<div class="container">

<h1>🛒 سلة المشتريات</h1>

{% if items %}

{% for item in items %}
<div class="item">

{% if item[3] %}
<img src="/static/uploads/{{ item[3] }}">
{% endif %}

<div class="info">
<h3>{{ item[1] }}</h3>
<div>السعر: {{ item[2] }} د.ع</div>
{% if item[5] %}<div>📏 المقاسات: {{ item[5] }}</div>{% endif %}
{% if item[6] %}<div>🎨 الألوان: {{ item[6] }}</div>{% endif %}


<form method="POST" action="/cart/update/{{ item[0] }}" class="qty">
<input
    type="number"
    name="quantity"
    value="{{ item[4] }}"
    min="1"
    style="width:60px;padding:8px;"
>
<button class="update">تحديث</button>
</form>

<form method="POST" action="/cart/remove/{{ item[0] }}" style="margin-top:8px;">
<button class="delete">🗑 حذف</button>
</form>

</div>

<div>
<strong>{{ item[2] * item[4] }} د.ع</strong>
</div>

</div>
{% endfor %}

<div class="total">
المجموع: {{ total }} د.ع

<a href="/checkout"
style="
display:block;
margin-top:15px;
padding:14px;
background:#16a34a;
color:white;
text-align:center;
text-decoration:none;
border-radius:10px;
font-size:18px;
">
📦 إتمام الطلب
</a>

</div>

<a href="/" class="back">← العودة للمتجر</a>

{% else %}

<div class="empty">
<h2>🛒 السلة فارغة</h2>
<p>ما عندك منتجات بالسلة حالياً.</p>
<a href="/" class="back">العودة للمتجر</a>
</div>

{% endif %}

</div>

</body>
</html>
""", items=items, total=total)


@app.route("/cart/update/<int:item_id>", methods=["POST"])
def update_cart(item_id):

    session_id = get_session_id()

    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 1

    quantity = max(1, quantity)

    conn = sqlite3.connect(DB)

    conn.execute(
        """
        UPDATE cart_items
        SET quantity = ?
        WHERE id = ? AND session_id = ?
        """,
        (quantity, item_id, session_id)
    )

    conn.commit()
    conn.close()

    return redirect("/cart")


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
def remove_from_cart(item_id):

    session_id = get_session_id()

    conn = sqlite3.connect(DB)

    conn.execute(
        "DELETE FROM cart_items WHERE id = ? AND session_id = ?",
        (item_id, session_id)
    )

    conn.commit()
    conn.close()

    return redirect("/cart")



# =========================
# إتمام الطلب من السلة
# =========================

@app.route("/checkout", methods=["GET", "POST"])
def checkout():

    session_id = get_session_id()

    conn = sqlite3.connect(DB)

    items = conn.execute("""
        SELECT
            cart_items.id,
            products.id,
            products.name,
            products.price,
            cart_items.quantity,
            cart_items.selected_sizes,
            cart_items.selected_colors,
            products.size,
            products.color
        FROM cart_items
        JOIN products ON products.id = cart_items.product_id
        WHERE cart_items.session_id = ?
        ORDER BY cart_items.id DESC
    """, (session_id,)).fetchall()

    if not items:
        conn.close()
        return redirect("/cart")

    total = sum(item[3] * item[4] for item in items)

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()

        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            latitude = None
            longitude = None

        if not name or not phone or not address:
            conn.close()

            return """
            <div style="font-family:Arial;text-align:center;padding:40px;">
                <h2>❌ يرجى ملء جميع المعلومات</h2>
                <a href="/checkout">العودة</a>
            </div>
            """

        # إنشاء الطلب الرئيسي
        first_product = items[0]

        cursor = conn.execute("""
            INSERT INTO orders
            (customer_name, phone, address, product_id, product_name,
             quantity, price, total, status, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            phone,
            address,
            first_product[1],
            "طلب متعدد المنتجات",
            sum(item[4] for item in items),
            0,
            total,
            "جديد",
            latitude,
            longitude
        ))

        order_id = cursor.lastrowid

        # إضافة تفاصيل المنتجات
        for item in items:

            conn.execute("""
                INSERT INTO order_items
                (order_id, product_id, product_name, quantity, price, total, size, color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                item[1],
                item[2],
                item[4],
                item[3],
                item[3] * item[4],
                item[5],
                item[6]
            ))

        # تفريغ السلة
        conn.execute(
            "DELETE FROM cart_items WHERE session_id = ?",
            (session_id,)
        )

        conn.commit()
        conn.close()

        return render_template_string("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>تم الطلب</title>
<style>
body{
    font-family:Arial;
    background:#f5f5f5;
    padding:20px;
}
.box{
    max-width:500px;
    margin:60px auto;
    background:white;
    padding:35px;
    border-radius:18px;
    text-align:center;
}
.success{
    font-size:60px;
}
a{
    display:block;
    margin-top:20px;
    padding:14px;
    background:#111827;
    color:white;
    text-decoration:none;
    border-radius:10px;
}
</style>
</head>
<body>

<div class="box">

<div class="success">✅</div>

<h1>تم استلام طلبك!</h1>

<p>رقم الطلب:</p>

<h2>#{{ order_id }}</h2>

<p>راح يتم تجهيز طلبك والتواصل وياك.</p>

<a href="/">العودة للمتجر</a>

</div>

</body>
</html>
""", order_id=order_id)

    return render_template_string("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>إتمام الطلب</title>
<style>
body{
    font-family:Arial;
    background:#f5f5f5;
    margin:0;
    padding:20px;
}
.box{
    max-width:600px;
    margin:auto;
}
.card{
    background:white;
    padding:20px;
    border-radius:16px;
    margin-bottom:15px;
}
input,textarea{
    width:100%;
    box-sizing:border-box;
    padding:13px;
    margin-top:8px;
    margin-bottom:15px;
    border:1px solid #ddd;
    border-radius:10px;
    font-size:16px;
}
textarea{
    min-height:100px;
}
button{
    width:100%;
    padding:15px;
    border:0;
    border-radius:10px;
    background:#16a34a;
    color:white;
    font-size:18px;
}
.product{
    display:flex;
    justify-content:space-between;
    margin:10px 0;
}
.total{
    font-size:21px;
    font-weight:bold;
    border-top:1px solid #ddd;
    padding-top:15px;
}
</style>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
</head>
<body>

<div class="box">

<h1>📦 إتمام الطلب</h1>

<div class="card">

<h2>🛒 المنتجات</h2>

{% for item in items %}

<div class="product" style="display:block; padding:12px 0; border-bottom:1px solid #eee;">
<strong style="display:block; font-size:18px; margin-bottom:8px;">
{{ item[2] }}
</strong>

<div style="font-size:15px; color:#555; line-height:1.8;">
📏 المقاس: {{ item[5] or "غير محدد" }}<br>
🎨 اللون: {{ item[6] or "غير محدد" }}<br>
🔢 الكمية: {{ item[4] }}
</div>

<strong style="display:block; margin-top:8px;">
{{ item[3] * item[4] }} د.ع
</strong>
</div>

{% endfor %}

<div class="total">
المجموع: {{ total }} د.ع
</div>

</div>

<form method="POST" class="card">

<h2>📋 معلومات التوصيل</h2>

<label>الاسم</label>
<input
    type="text"
    name="name"
    placeholder="اكتب اسمك"
    required
>

<label>رقم الهاتف</label>
<input
    type="tel"
    name="phone"
    placeholder="07xxxxxxxxx"
    required
>
<label>📍 موقع التوصيل</label>

<input type="hidden" name="latitude" id="latitude">
<input type="hidden" name="longitude" id="longitude">

<div id="map" style="
    width:100%;
    height:350px;
    border-radius:14px;
    margin:10px 0;
    overflow:hidden;
    border:1px solid #ddd;
"></div>

<p id="locationStatus" style="text-align:center;color:#555;">
    اضغط على الخريطة لتحديد موقع التوصيل
</p>

<label>العنوان</label>
<textarea
    name="address"
    placeholder="المحافظة، المنطقة، الشارع..."
    required
></textarea>



<button type="button" onclick="getLocation()" style="
    background:#2563eb;
    color:white;
    border:none;
    padding:14px;
    border-radius:10px;
    width:100%;
    font-size:16px;
    margin:10px 0;
">
    📍 تحديد موقعي
</button>

<button type="submit">
✅ تأكيد الطلب
</button>

</form>

</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
const defaultLat = 33.3152;
const defaultLng = 44.3661;

const map = L.map("map").setView([defaultLat, defaultLng], 12);

L.tileLayer("https://tile.openstreetmap.de/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map);

let marker = null;

function setLocation(lat, lng) {
    document.getElementById("latitude").value = lat;
    document.getElementById("longitude").value = lng;

    if (marker) {
        marker.setLatLng([lat, lng]);
    } else {
        marker = L.marker([lat, lng]).addTo(map);
    }

    document.getElementById("locationStatus").innerText =
        "✅ تم تحديد موقع التوصيل";
}

map.on("click", function(e) {
    setLocation(e.latlng.lat, e.latlng.lng);
});

function getLocation() {
    const status = document.getElementById("locationStatus");

    if (!navigator.geolocation) {
        status.innerText = "❌ جهازك لا يدعم تحديد الموقع";
        return;
    }

    status.innerText = "📍 جاري تحديد موقعك...";

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;

            map.setView([lat, lng], 17);
            setLocation(lat, lng);
        },
        function() {
            status.innerText =
                "❌ لم يتم السماح بالوصول إلى موقعك";
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}
</script>
</body>
</html>
""", items=items, total=total)


# =========================
# تسجيل الدخول
# =========================

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if session.get("admin"):
        return redirect("/dashboard")

    error = False

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect("/dashboard")

        error = True

    return render_template_string(
        LOGIN_HTML,
        error=error
    )


# =========================
# لوحة التحكم
# =========================

@app.route("/dashboard")
def dashboard():

    if not admin_required():
        return redirect("/admin")

    conn = sqlite3.connect(DB)

    products = conn.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    product_count = conn.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    order_count = conn.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    new_orders = conn.execute(
        "SELECT COUNT(*) FROM orders WHERE status = ?",
        ("جديد",)
    ).fetchone()[0]

    total_sales = conn.execute(
        "SELECT COALESCE(SUM(total), 0) FROM orders "
        "WHERE status != ?",
        ("ملغي",)
    ).fetchone()[0]

    orders = conn.execute("""
        SELECT id, customer_name, phone, address,
               product_name, quantity, price, total,
               status, created_at, latitude, longitude
        FROM orders
        ORDER BY id DESC
    """).fetchall()

    order_items = {}

    for order in orders:
        order_items[order[0]] = conn.execute("""
            SELECT product_name, quantity, price, total, size, color
            FROM order_items
            WHERE order_id = ?
            ORDER BY id ASC
        """, (order[0],)).fetchall()

    conn.close()

    return render_template_string(
        ADMIN_HTML,
        products=products,
        product_count=product_count,
        order_count=order_count,
        new_orders=new_orders,
        total_sales=total_sales,
        orders=orders,
        order_items=order_items
    )


# =========================
# إضافة منتج
# =========================

@app.route("/add", methods=["POST"])
def add():

    if not admin_required():
        return redirect("/admin")

    name = request.form["name"]

    price = float(
        request.form["price"]
    )

    sizes = request.form.getlist("sizes")
    colors = request.form.getlist("colors")

    size = ", ".join(sizes)
    color = ", ".join(colors)

    category = request.form.get("category", "أخرى")

    image = request.files.get("image")
    image2 = request.files.get("image2")
    image3 = request.files.get("image3")

    filename = ""
    filename2 = ""
    filename3 = ""

    if image and image.filename:
        ext = os.path.splitext(
            image.filename
        )[1].lower()

        filename = str(
            uuid.uuid4()
        ) + ext

        image.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename
            )
        )

    if image2 and image2.filename:
        ext = os.path.splitext(
            image2.filename
        )[1].lower()

        filename2 = str(
            uuid.uuid4()
        ) + ext

        image2.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename2
            )
        )

    if image3 and image3.filename:
        ext = os.path.splitext(
            image3.filename
        )[1].lower()

        filename3 = str(
            uuid.uuid4()
        ) + ext

        image3.save(
            os.path.join(
                UPLOAD_FOLDER,
                filename3
            )
        )

    conn = sqlite3.connect(DB)

    conn.execute("""
        INSERT INTO products
        (name, price, size, color, image, image2, image3, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        price,
        size,
        color,
        filename,
        filename2,
        filename3,
          category
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================
# حذف منتج
# =========================

@app.route(
    "/delete/<int:product_id>",
    methods=["POST"]
)
def delete(product_id):

    if not admin_required():
        return redirect("/admin")

    conn = sqlite3.connect(DB)

    product = conn.execute(
        "SELECT image FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    conn.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    conn.commit()
    conn.close()

    if product and product[0]:

        path = os.path.join(
            UPLOAD_FOLDER,
            product[0]
        )

        if os.path.exists(path):
            os.remove(path)

    return redirect("/dashboard")


# =========================
# تسجيل الخروج
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================
# تشغيل النظام
# =========================
# =========================
# تحديث حالة الطلب
# =========================

@app.route("/update_order/<int:order_id>", methods=["POST"])
def update_order(order_id):

    if not admin_required():
        return redirect("/admin")

    status = request.form.get("status", "جديد")

    allowed_statuses = {
        "جديد",
        "قيد التجهيز",
        "تم التسليم",
        "ملغي"
    }

    if status not in allowed_statuses:
        status = "جديد"

    conn = sqlite3.connect(DB)

    conn.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (status, order_id)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================
# تفاصيل الطلب
# =========================

@app.route("/order/<int:order_id>")
def order_details(order_id):

    if not admin_required():
        return redirect("/admin")

    conn = sqlite3.connect(DB)

    order = conn.execute("""
        SELECT id, customer_name, phone, address,
               product_name, quantity, price, total,
               status, created_at, latitude, longitude
        FROM orders
        WHERE id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        return redirect("/dashboard")

    items = conn.execute("""
        SELECT product_name, quantity, price, total
        FROM order_items
        WHERE order_id = ?
        ORDER BY id ASC
    """, (order_id,)).fetchall()

    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<title>تفاصيل الطلب #{{ order[0] }}</title>

<style>
body {
    margin: 0;
    background: #f4f4f5;
    font-family: Arial;
    padding: 20px;
}

.container {
    max-width: 700px;
    margin: auto;
}

.box {
    background: white;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}

h1 {
    margin-top: 0;
}

.info {
    line-height: 1.9;
}

.item {
    background: #f9fafb;
    padding: 14px;
    border-radius: 10px;
    margin-top: 10px;
    display: flex;
    justify-content: space-between;
    gap: 10px;
}

.total {
    background: #111827;
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin-top: 15px;
    font-size: 20px;
    font-weight: bold;
}

.back {
    display: block;
    text-align: center;
    background: #111827;
    color: white;
    padding: 13px;
    border-radius: 10px;
    text-decoration: none;
}
</style>

</head>

<body>

<div class="container">

<div class="box">

<h1>🧾 طلب رقم #{{ order[0] }}</h1>

<div class="info">

<p>👤 <b>اسم الزبون:</b> {{ order[1] }}</p>

<p>📞 <b>رقم الهاتف:</b> {{ order[2] }}</p>

<p>📍 <b>العنوان:</b> {{ order[3] }}</p>

<p>📊 <b>الحالة:</b> {{ order[8] }}</p>

<p>🕐 <b>تاريخ الطلب:</b> {{ order[9] }}</p>

</div>

</div>


<div class="box">

<h2>🛍️ المنتجات</h2>

{% for item in items %}

<div class="item">

<div>
<b>{{ item[0] }}</b>
<br>
الكمية: {{ item[1] }}
</div>

<div>
{{ item[3] }} د.ع
</div>

</div>

{% endfor %}

<div class="total">
💰 المجموع: {{ order[7] }} د.ع
</div>

</div>


<a href="/dashboard" class="back">
← العودة للوحة التحكم
</a>

</div>

</body>
</html>
""", order=order, items=items)


# =========================
# حذف طلب
# =========================

@app.route("/delete_order/<int:order_id>", methods=["POST"])
def delete_order(order_id):

    if not admin_required():
        return redirect("/admin")

    conn = sqlite3.connect(DB)

    conn.execute(
        "DELETE FROM order_items WHERE order_id = ?",
        (order_id,)
    )

    conn.execute(
        "DELETE FROM orders WHERE id = ?",
        (order_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# =========================
# صفحة شراء المنتج
# =========================

BUY_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<title>إتمام الطلب</title>

<style>

body {
    margin: 0;
    font-family: Arial;
    background: #f4f4f5;
}

.box {
    max-width: 500px;
    margin: 40px auto;
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 3px 15px #0002;
}

input {
    width: 100%;
    padding: 14px;
    margin: 8px 0;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 16px;
}

button {
    width: 100%;
    padding: 14px;
    border: 0;
    border-radius: 10px;
    background: #111827;
    color: white;
    font-size: 16px;
    margin-top: 10px;
}

.product {
    background: #f9fafb;
    padding: 15px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.total {
    font-size: 20px;
    font-weight: bold;
}

</style>

</head>

<body>

<div class="box">

<h2>🛒 إتمام الطلب</h2>

<div class="product">

<h3>{{ product[1] }}</h3>

<p>💰 السعر: {{ product[2] }} د.ع</p>

<p>📏 المقاسات: {{ product[3] or "غير محدد" }}</p>

<p>🎨 اللون: {{ product[4] or "غير محدد" }}</p>

</div>

<form method="POST">

<input
name="customer_name"
placeholder="👤 اسمك"
required>

<input
name="phone"
type="tel"
placeholder="📱 رقم الهاتف"
required>

<input
name="address"
placeholder="📍 العنوان"
required>

<input type="hidden" name="latitude" id="latitude">
<input type="hidden" name="longitude" id="longitude">

<button type="button" onclick="getLocation()" style="background:#2563eb;color:white;border:0;padding:14px;border-radius:10px;width:100%;font-size:16px;margin:10px 0;">
📍 تحديد موقعي
</button>

<div id="location-status" style="padding:10px;margin:10px 0;background:#f3f4f6;border-radius:10px;text-align:center;">
لم يتم تحديد الموقع بعد
</div>

<div id="map" style="height:300px;width:100%;border-radius:12px;margin:10px 0;"></div>

<input
name="quantity"
type="number"
min="1"
value="1"
placeholder="الكمية"
required>

<button type="submit">
✅ تأكيد الطلب
</button>

</form>

</div>

<script>
let map = L.map("map").setView([33.3152, 44.3661], 12);
L.tileLayer("https://tile.openstreetmap.de/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap"
}).addTo(map);

let marker = null;

function setLocation(lat, lng) {
    document.getElementById("latitude").value = lat;
    document.getElementById("longitude").value = lng;

    if (marker) {
        map.removeLayer(marker);
    }

    marker = L.marker([lat, lng]).addTo(map);
    map.setView([lat, lng], 17);

    document.getElementById("location-status").innerHTML = "✅ تم تحديد موقع التوصيل";
}

function getLocation() {
    if (!navigator.geolocation) {
        document.getElementById("location-status").innerHTML = "❌ تحديد الموقع غير مدعوم";
        return;
    }

    document.getElementById("location-status").innerHTML = "⏳ جاري تحديد موقعك...";

    navigator.geolocation.getCurrentPosition(
        function(position) {
            setLocation(
                position.coords.latitude,
                position.coords.longitude
            );
        },
        function() {
            document.getElementById("location-status").innerHTML = "❌ اسمح للمتصفح بالوصول إلى موقعك";
        },
        {
            enableHighAccuracy: true,
            timeout: 15000,
            maximumAge: 0
        }
    );
}

map.on("click", function(e) {
    setLocation(e.latlng.lat, e.latlng.lng);
});
</script>
</body>
</html>
"""


# =========================
# شراء منتج
# =========================

@app.route(
    "/buy/<int:product_id>",
    methods=["GET", "POST"]
)
def buy(product_id):

    conn = sqlite3.connect(DB)

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    conn.close()

    if not product:
        return "❌ المنتج غير موجود", 404

    if request.method == "POST":

        customer_name = request.form.get(
            "customer_name", ""
        ).strip()

        phone = request.form.get(
            "phone", ""
        ).strip()

        address = request.form.get(
            "address", ""
        ).strip()

        latitude = request.form.get("latitude") or None
        longitude = request.form.get("longitude") or None

        try:
            latitude = float(latitude) if latitude else None
        except ValueError:
            latitude = None

        try:
            longitude = float(longitude) if longitude else None
        except ValueError:
            longitude = None
        try:
            quantity = int(
                request.form.get(
                    "quantity", 1
                )
            )
        except ValueError:
            quantity = 0

        if quantity < 1:
            return "❌ الكمية غير صحيحة", 400

        total = product[2] * quantity

        conn = sqlite3.connect(DB)

        conn.execute("""
            INSERT INTO orders
            (
                customer_name,
                phone,
                address,
                product_id,
                product_name,
                quantity,
                price,
                total,
                status,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_name,
            phone,
            address,
            product[0],
            product[1],
            quantity,
            product[2],
            total,
            "جديد",
            latitude,
            longitude
        ))

        conn.commit()
        conn.close()

        return """
        <!DOCTYPE html>
        <html lang="ar" dir="rtl">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport"
        content="width=device-width, initial-scale=1.0">
        <title>تم الطلب</title>

        <style>
        body {
            font-family: Arial;
            background: #f4f4f5;
            text-align: center;
            padding: 50px 20px;
        }

        .box {
            max-width: 500px;
            margin: auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
        }

        a {
            display: block;
            background: #111827;
            color: white;
            padding: 14px;
            border-radius: 10px;
            text-decoration: none;
            margin-top: 20px;
        }
        </style>

        </head>

        <body>

        <div class="box">

        <h1>✅ تم إرسال طلبك</h1>

        <p>
        شكرًا لطلبك ❤️
        </p>

        <a href="/">
        🏠 الرجوع للمتجر
        </a>

        </div>

        </body>
        </html>
        """

    return render_template_string(
        BUY_HTML,
        product=product
    )
# =========================
# صفحة طلبات الزبائن
# =========================

ORDERS_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>
<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>طلبات الزبائن</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial;
    background: #f4f4f5;
}

header {
    background: #111827;
    color: white;
    padding: 20px;
    text-align: center;
}

.container {
    max-width: 1000px;
    margin: auto;
    padding: 20px;
}

.order {
    background: white;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
    box-shadow: 0 3px 12px #0001;
}

.row {
    margin: 8px 0;
}

.status {
    display: inline-block;
    background: #f3f4f6;
    padding: 8px 12px;
    border-radius: 8px;
    font-weight: bold;
}

button {
    width: 100%;
    padding: 13px;
    border: 0;
    border-radius: 10px;
    background: #111827;
    color: white;
    font-size: 16px;
    margin-top: 10px;
}

.back {
    background: #6b7280;
}

select {
    width: 100%;
    padding: 13px;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 16px;
}

.delete {
    background: #dc2626;
}

</style>

</head>

<body>

<header>

<h1>📦 طلبات الزبائن</h1>

</header>

<div class="container">
<div style="
display:grid;
grid-template-columns:
repeat(auto-fit,minmax(180px,1fr));
gap:15px;
margin-bottom:20px;
">

<div style="
background:white;
padding:20px;
border-radius:15px;
text-align:center;
box-shadow:0 3px 12px #0001;
">

<h2>🛍️</h2>

<h3>المنتجات</h3>

<p style="font-size:25px;font-weight:bold;">
{{ product_count }}
</p>

</div>


<div style="
background:white;
padding:20px;
border-radius:15px;
text-align:center;
box-shadow:0 3px 12px #0001;
">

<h2>📦</h2>

<h3>كل الطلبات</h3>

<p style="font-size:25px;font-weight:bold;">
{{ order_count }}
</p>

</div>


<div style="
background:white;
padding:20px;
border-radius:15px;
text-align:center;
box-shadow:0 3px 12px #0001;
">

<h2>🆕</h2>

<h3>طلبات جديدة</h3>

<p style="
font-size:25px;
font-weight:bold;
color:#dc2626;
">
{{ new_orders }}
</p>

</div>


<div style="
background:white;
padding:20px;
border-radius:15px;
text-align:center;
box-shadow:0 3px 12px #0001;
">

<h2>💰</h2>

<h3>إجمالي المبيعات</h3>

<p style="font-size:22px;font-weight:bold;">
{{ total_sales }} د.ع
</p>

</div>

</div>


<div class="box">

<a href="/orders"
style="
display:block;
text-align:center;
text-decoration:none;
background:#111827;
color:white;
padding:15px;
border-radius:10px;
font-size:18px;
">

📦 إدارة طلبات الزبائن

</a>

</div>

{% if orders %}

{% for o in orders %}

<div class="order">

<h2>🧾 طلب رقم #{{ o[0] }}</h2>

<div class="row">
👤 <b>الزبون:</b> {{ o[1] }}
</div>

<div class="row">
📱 <b>الهاتف:</b> {{ o[2] }}
</div>

<div class="row">
📍 <b>العنوان:</b> {{ o[3] }}
</div>

<hr>

<div class="row">
👕 <b>المنتج:</b> {{ o[5] }}
</div>

<div class="row">
🔢 <b>الكمية:</b> {{ o[6] }}
</div>

<div class="row">
💰 <b>السعر:</b> {{ o[7] }} د.ع
</div>

<div class="row">
💵 <b>المجموع:</b> {{ o[8] }} د.ع
</div>

<div class="row">
🕐 <b>وقت الطلب:</b> {{ o[10] }}
</div>

<p class="status">
📌 الحالة: {{ o[9] }}
</p>

<form method="POST"
action="/order-status/{{ o[0] }}">

<select name="status">

<option value="جديد"
{% if o[9] == "جديد" %}selected{% endif %}>
🆕 جديد
</option>

<option value="قيد التجهيز"
{% if o[9] == "قيد التجهيز" %}selected{% endif %}>
🔄 قيد التجهيز
</option>

<option value="تم التسليم"
{% if o[9] == "تم التسليم" %}selected{% endif %}>
✅ تم التسليم
</option>

<option value="ملغي"
{% if o[9] == "ملغي" %}selected{% endif %}>
❌ ملغي
</option>

</select>

<button type="submit">
💾 تحديث الحالة
</button>

</form>

<form method="POST"
action="/delete-order/{{ o[0] }}">

<button class="delete"
type="submit"
onclick="return confirm('حذف هذا الطلب؟')">

🗑️ حذف الطلب

</button>

</form>

</div>

{% endfor %}

{% else %}

<div class="order">

<h2>📭 ماكو طلبات حاليًا</h2>

<p>
لما يشتري أحد من المتجر، راح يظهر طلبه هنا.
</p>

</div>

{% endif %}


<form action="/dashboard">

<button class="back">
⬅️ الرجوع للوحة التحكم
</button>

</form>

</div>

</body>

</html>
"""


@app.route("/orders")
def orders():

    if not admin_required():
        return redirect("/admin")

    conn = sqlite3.connect(DB)

    orders = conn.execute("""
        SELECT *
        FROM orders
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template_string(
        ORDERS_HTML,
        orders=orders
    )


# =========================
# تغيير حالة الطلب
# =========================

@app.route(
    "/order-status/<int:order_id>",
    methods=["POST"]
)
def order_status(order_id):

    if not admin_required():
        return redirect("/admin")

    status = request.form.get(
        "status",
        "جديد"
    )

    allowed = [
        "جديد",
        "قيد التجهيز",
        "تم التسليم",
        "ملغي"
    ]

    if status not in allowed:
        return redirect("/orders")

    conn = sqlite3.connect(DB)

    conn.execute("""
        UPDATE orders
        SET status = ?
        WHERE id = ?
    """, (
        status,
        order_id
    ))

    conn.commit()
    conn.close()

    return redirect("/orders")


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
