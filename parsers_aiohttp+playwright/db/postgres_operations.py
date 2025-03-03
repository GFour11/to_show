from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres_models import LondonApartment, NetherlandApartment


class DbOperator:

    def __init__(self, class_):
        self.class_ = class_

    async def find_duplicates(self, session: AsyncSession, apartments):
        all_apartments = await session.execute(select(self.class_))
        all_apartments = all_apartments.scalars().all()
        if all_apartments:
            apartment_source_link = [apartment.link for apartment in all_apartments]
            filtered_apartments = [
                apartment
                for apartment in apartments
                if apartment.get("link") not in apartment_source_link
            ]
            return filtered_apartments
        else:
            return apartments

    async def add_to_db(self, session: AsyncSession, kwargs_data):
        to_insert = [self.class_(**kwargs) for kwargs in kwargs_data]
        try:
            session.add_all(to_insert)
            await session.commit()
            return f"{len(to_insert)} objects was added.", [
                obj.to_dict() for obj in to_insert
            ]
        except SQLAlchemyError as e:
            await session.rollback()
            return f"Finished with Error{e}"


netherland = DbOperator(NetherlandApartment)
london = DbOperator(LondonApartment)
