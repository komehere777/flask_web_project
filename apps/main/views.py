from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from apps.main.models import Product
from apps.personal.models import Wishlist
from apps.app import db
from apps.main.forms import ModelCapacityForm, EmptyForm  # CSRF 토큰을 위한 빈 폼
import pandas as pd
import requests

main = Blueprint("main", __name__, template_folder="templates", static_folder="static")


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
        print(query)
        # query를 값만 연결된 문자열로 변환
        query_str = " ".join([f"{value}" for key, value in query.items()])
        print(query_str)
        # GB 제거 replace
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

        # 검색시작
        try:
            url = f"https://api.bunjang.co.kr/api/1/find_v2.json?q={query_str}&order=score&page=1&request_id=2024704081724&f_category_id=600700001&stat_device=w&n=100&stat_category_required=1&req_ref=search&version=5"
            # Request API
            response = requests.get(url)
            data = response.json()

            ipdf = pd.DataFrame(data["list"])[columns]

            # product_image 컬럼을 이미지 태그로 변환
            ipdf["product_image"] = ipdf["product_image"].apply(
                lambda x: (
                    f'<img src="{x}" alt="Product Image" width="100">'
                    if pd.notnull(x)
                    else ""
                )
            )

        except Exception as e:
            print(f"검색어 입력오류: {e}")
            ipdf = pd.DataFrame(columns=columns)

        # nan값 제거
        ipdf = ipdf.dropna(subset=["location", "name", "price"])

        # 제외어
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
        ipdf = ipdf[["name", "price", "product_image", "location", "update_time"]]
        ipdf["update_time"] = ipdf["update_time"].sort_values(ascending=False)

        # 데이터베이스에 저장
        for index, row in ipdf.iterrows():
            product = Product(
                NAME=row["name"],
                PRICE=row["price"],
                PRODUCT_IMAGE=row["product_image"],
                LOCATION=row["location"],
                DELTA_TIME=row["update_time"],
            )
            db.session.add(product)
        db.session.commit()

        # HTML 변환
        ipdf_html = ipdf.to_html(
            classes="table table-striped", index=False, escape=False
        )

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(
                success=True, model=model, capacity=capacity, table=ipdf_html
            )

    products = Product.query.limit(5).all()  # 상위 5개의 제품만 가져옵니다.
    return render_template(
        "main/index.html",
        products=products,
        user=current_user,
        form=form,
        ipdf_html=ipdf_html,
    )


@main.route("/product/<int:product_id>")
@login_required
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
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
    return redirect(url_for("main.product_detail", product_id=product_id))


@main.route("/api/get_product_id")
def get_product_id():
    product_name = request.args.get("name")
    product = Product.query.filter_by(NAME=product_name).first()
    if product:
        return jsonify({"id": product.ID})
    return jsonify({"error": "Product not found"}), 404
