import pandas as pd
from datetime import datetime
from apps.app import db
import uuid


class Product(db.Model):
    __tablename__ = 'product'

    ID = db.Column(db.Integer, primary_key=True)
    NAME = db.Column(db.String, nullable=False)
    PRICE = db.Column(db.Float, nullable=False)
    PRODUCT_IMAGE = db.Column(db.String, nullable=True)
    LOCATION = db.Column(db.String, nullable=False)
    DELTA_TIME = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f'<Product {self.NAME}>'

    @staticmethod
    def load_csv_to_db(file_path):
        data = pd.read_csv(file_path)
        for index, row in data.iterrows():
            product = Product(
                ID=uuid.uuid4().int & (1 << 31) - 1,  # Generates a random ID
                NAME=row['NAME'],
                PRICE=row['PRICE'],
                PRODUCT_IMAGE=row['PRODUCT_IMAGE'] if 'PRODUCT_IMAGE' in row and pd.notna(
                    row['PRODUCT_IMAGE']) else None,
                LOCATION=row['LOCATION'],
                DELTA_TIME=row['DELTA_TIME'] if 'DELTA_TIME' in row and pd.notna(row['DELTA_TIME']) else None
                # 변경: datetime에서 문자열로
            )
            db.session.add(product)
        db.session.commit()
