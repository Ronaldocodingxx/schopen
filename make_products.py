import csv
import json

INPUT = "datafeed_2643060.csv"
OUTPUT = "products.json"

MAX_ITEMS = 1000

products = []

with open(INPUT, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter=",")
    for row in reader:
        # Hauptbild + zusätzliche Bilder
        main_img = (
            row.get("merchant_image_url")
            or row.get("aw_image_url")
            or row.get("large_image")
            or ""
        )

        extra_imgs = [
            row.get("large_image"),
            row.get("alternate_image"),
            row.get("alternate_image_two"),
            row.get("alternate_image_three"),
            row.get("alternate_image_four"),
        ]

        # Alles zusammen in ein sauberes Array packen
        images = []
        for url in [main_img] + extra_imgs:
            url = (url or "").strip()
            if not url:
                continue
            if url not in images:
                images.append(url)

        # Ohne Bild oder ohne Deep-Link → überspringen
        if not images:
            continue
        if not row.get("aw_deep_link"):
            continue

        pid = (
            row.get("aw_product_id")
            or row.get("merchant_product_id")
            or row.get("data_feed_id")
            or ""
        ).strip()

        title = (row.get("product_name") or "").strip()
        description = (row.get("description") or "").strip()
        price = (row.get("search_price") or row.get("store_price") or "").strip()
        merchant = (row.get("merchant_name") or "").strip()
        category = (row.get("merchant_category") or "").strip()
        deeplink = (row.get("aw_deep_link") or "").strip()

        if not pid or not title:
            continue

        # CHF dazu, falls nicht drin
        subtitle_parts = []
        if price:
            if "CHF" not in price:
                subtitle_parts.append(f"CHF {price}")
            else:
                subtitle_parts.append(price)
        if merchant:
            subtitle_parts.append(merchant)

        subtitle = " • ".join(subtitle_parts)

        products.append(
            {
                "id": pid,
                "title": title,
                "subtitle": subtitle,
                "price": price,
                "image": images[0],   # erstes Bild als Hauptbild
                "images": images,     # alle Bilder für das Karussell
                "deeplink": deeplink,
                "merchant": merchant,
                "category": category,
                "description": description,
            }
        )

        if len(products) >= MAX_ITEMS:
            break

with open(OUTPUT, "w", encoding="utf-8") as out:
    json.dump(products, out, ensure_ascii=False, indent=2)

print(f"Fertig! {len(products)} Produkte in {OUTPUT} geschrieben.")
