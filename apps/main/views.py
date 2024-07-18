# main/views.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from apps.main.models import Product
from apps.personal.models import Wishlist
from apps.app import db
from apps.main.forms import ModelCapacityForm, EmptyForm  # CSRF 토큰을 위한 빈 폼
import pandas as pd
import requests
import urllib.parse

main = Blueprint("main", __name__, template_folder="templates", static_folder="static")


def normalize_name(name):
    return name.replace(" ", "").replace("-", "").replace("_", "").lower()


def dataframe_to_html(df):
    html = '<table class="table table-striped">\n'
    html += "<thead>\n<tr>"
    for column in ['제목', '가격', '이미지', '위치', '시간']:
        html += f"<th>{column}</th>"
    html += "</tr>\n</thead>\n<tbody>\n"

    for _, row in df.iterrows():
        html += f'<tr data-product-id="{row["pid"]}">'
        for column in df.columns[[1,2,3,4,5]]:
            value = row[column]
            if column == "product_image":
                html += f'<td><img src="{value}" alt="Product Image" width="100"></td>'
            else:
                html += f"<td>{value}</td>"

        html += "</tr>\n"

    html += "</tbody>\n</table>"
    return html


@main.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ModelCapacityForm()
    query = {}
    ipdf_html = None
    if form.validate_on_submit():
        model = request.form.get("modelSelect")
        capacity = request.form.get("capacitySelect")
        query["model"] = model
        query["capacity"] = capacity
        query_str = " ".join([f"{value}" for key, value in query.items()])
        query_str = query_str.replace("GB", "")
        columns = [
            "category_id",
            "name",
            "product_image",
            "pid",
            "price",
            "update_time",
            "location",
        ]

        # 검색 시작
        try:
            url = f"https://api.bunjang.co.kr/api/1/find_v2.json?q={query_str}&order=score&page=1&request_id=2024704081724&f_category_id=600700001&stat_device=w&n=100&stat_category_required=1&req_ref=search&version=5"
            response = requests.get(url)
            data = response.json()
            ipdf = pd.DataFrame(data["list"])[columns]
        except Exception as e:
            print(f"검색어 입력오류: {e}")
            ipdf = pd.DataFrame(columns=columns)

        # nan값 제거
        ipdf = ipdf.dropna(subset=["location", "name", "price"])
        ipdf = ipdf[ipdf["location"] != ""]

        # 제외어 필터링
        exclude_keywords = [
            "교환",
            "매입",
            "삽니다",
            "구합니다",
            "도매",
            "대량",
            "대여",
            "정리",
            "수리",
            "공시",
        ]
        for keyword in exclude_keywords:
            ipdf = ipdf[~ipdf["name"].str.contains(keyword, na=False)]

        # name price product_image location update_time 만 사용
        ipdf = ipdf[
            ["pid", "name", "price", "product_image", "location", "update_time"]
        ]
        ipdf["update_time"] = (
            ipdf["update_time"].astype(str).sort_values(ascending=False)
        )

        # 데이터베이스에 저장
        for index, row in ipdf.iterrows():
            existing_product = Product.query.filter_by(PID=row["pid"]).first()
            if existing_product:
                existing_product.NAME = normalize_name(row["name"])
                existing_product.PRICE = row["price"]
                existing_product.PRODUCT_IMAGE = urllib.parse.unquote(
                    row["product_image"]
                )
                existing_product.LOCATION = row["location"]
                existing_product.DELTA_TIME = row["update_time"]
            else:
                product = Product(
                    PID=row["pid"],
                    NAME=normalize_name(row["name"]),
                    PRICE=row["price"],
                    PRODUCT_IMAGE=urllib.parse.unquote(
                        row["product_image"]
                    ),  # URL 디코딩하여 저장
                    LOCATION=row["location"],
                    DELTA_TIME=row["update_time"],
                )
                db.session.add(product)
        db.session.commit()

        # HTML 변환
        ipdf_html = dataframe_to_html(ipdf)

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                success=True, model=model, capacity=capacity, table=ipdf_html
            )

    products = Product.query.limit(5).all()
    return render_template(
        "main/index.html",
        products=products,
        user=current_user,
        form=form,
        ipdf_html=ipdf_html,
    )


@main.route("/product/<int:pid>")
@login_required
def product_detail(pid):
    product = Product.query.filter_by(PID=pid).first()
    print(f'프로덕트 디테일 확인 콘솔:{product}')
    if product is None:
        flash("Product not found.")
        return redirect(url_for("main.index"))
    form = EmptyForm()
    return render_template(
        "main/product_detail.html", product=product, user=current_user, form=form
    )


@main.route("/product/<int:product_id>/wishlist", methods=["POST"])
@login_required
def add_to_wishlist(product_id):
    form = EmptyForm()
    if form.validate_on_submit():
        product = Product.query.get_or_404(product_id)
        if Wishlist.query.filter_by(
            user_id=current_user.id, product_id=product_id
        ).first():
            flash("This product is already in your wishlist.")
        else:
            wishlist_item = Wishlist(user_id=current_user.id, product_id=product_id)
            db.session.add(wishlist_item)
            db.session.commit()
            flash("Product added to wishlist.")
    else:
        flash("Invalid CSRF token")
    return redirect(url_for("main.product_detail", pid=product_id))


@main.route("/api/get_product_pid")
def get_product_pid():
    pid = request.args.get("pid")
    product = Product.query.filter(Product.PID == pid).first()
    if product:
        return jsonify({"id": product.ID})
    return jsonify({"error": "Product not found"}), 404
