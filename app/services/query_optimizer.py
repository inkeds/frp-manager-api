from typing import Any, List, Optional, Type, TypeVar
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import Select
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class QueryOptimizer:
    @staticmethod
    def paginate(
        query: Select,
        page: int = 1,
        per_page: int = 10
    ) -> Select:
        """分页优化"""
        return query.offset((page - 1) * per_page).limit(per_page)

    @staticmethod
    def with_count(db: Session, query: Select) -> tuple[List[Any], int]:
        """获取查询结果及总数"""
        count = db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        results = db.scalars(query).all()
        return results, count

    @staticmethod
    def optimize_query(
        model: Type[ModelType],
        *relations: str,
        **filters: Any
    ) -> Select:
        """优化查询，自动加载关系"""
        query = select(model)
        
        # 添加关系预加载
        for relation in relations:
            query = query.options(joinedload(getattr(model, relation)))
        
        # 添加过滤条件
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(model, key) == value)
        
        return query

    @staticmethod
    def batch_query(
        db: Session,
        model: Type[ModelType],
        ids: List[int],
        batch_size: int = 100
    ) -> List[ModelType]:
        """批量查询优化"""
        results = []
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_results = db.scalars(
                select(model).filter(model.id.in_(batch_ids))
            ).all()
            results.extend(batch_results)
        return results

    @staticmethod
    def search_query(
        model: Type[ModelType],
        search_term: str,
        *search_fields: str,
        case_sensitive: bool = False
    ) -> Select:
        """搜索查询优化"""
        query = select(model)
        if search_term and search_fields:
            conditions = []
            for field in search_fields:
                column = getattr(model, field)
                if not case_sensitive:
                    conditions.append(
                        func.lower(column).contains(
                            search_term.lower()
                        )
                    )
                else:
                    conditions.append(
                        column.contains(search_term)
                    )
            query = query.filter(
                func.or_(*conditions)
            )
        return query
