from ast import arg
from typing import Annotated

import aiosqlite
from fastapi import Depends

from shared.database.db import get_db
from product_catalog_context.infrastructure.aiosqlite_repository.errors_mapper import map_errors


class DbRepository:
	def __init__(self, db : aiosqlite.Connection, name='', mapper=None):
		self.db = db
		self.name = name
		self.mapper=mapper

	async def _select(self, table_name, filters_dict=None, all=False):
		if filters_dict is None:
			filters_dict = {}
		query = f'SELECT * FROM {table_name} '
		conditions = []
		values = []
		for filter_key, filter_value in filters_dict.items():
			if filter_value is None:
				break
			conditions.append(f'{filter_key} = ?')
			values.append(filter_value)
		if len(conditions) > 0:
			query += 'WHERE '
			query += ' and '.join(conditions) + ';'
		try:
			async with self.db.execute(query, values) as cursor:
				if all == True:
					rows = await cursor.fetchall()
				else:
					rows = await cursor.fetchone()
		except Exception as e:
			raise map_errors(e) from e
		
				
		return rows
	
	async def delete(self, id, **filters):
		q = f'DELETE FROM {self.name} WHERE '
		if type(id) is list:
			if not id:
				return 0
			conditions = [' id  = ? ' for _ in id]
			q += ' OR '.join(conditions)
			args = id
		else:
			q += 'id = ?'
			args = [id]
		cursor = None
		try:
			cursor = await self._exec(q, args)
			return cursor.rowcount
		except Exception as e:
			raise map_errors(e) from e
		finally:
			if cursor is not None:
				await cursor.close()

	async def insert(self, obj, **options):
		return_obj = options.get('return_obj')
		if type(obj) is list:
			if not obj:
				return None
			if self.mapper is not None:
				obj_list = [self.mapper.to_storage_dict(o) for o in obj]
			else:
				obj_list = [o.model_dump() for o in obj]
			columns = obj_list[0].keys()
			question_marks = [['?'] * len(obj) for obj in obj_list]
			insert_rows = ['(' + ','.join(row) + ')' for row in question_marks]
			value_fields = ','.join(insert_rows)
			vals = [value for obj in obj_list for value in obj.values()]
		else:
			if self.mapper is not None:
				fields_dict = self.mapper.to_storage_dict(obj)
			else:
				fields_dict = obj.model_dump()
			columns = fields_dict.keys()
			question_marks = ', '.join(['?' for _ in columns])
			value_fields = '(' + question_marks + ')'
			vals = list(fields_dict.values())
		#print(vals)
		q = f'INSERT INTO {self.name} (' + ', '.join(columns) + ') VALUES '
		q +=  value_fields
		q += f" RETURNING id, {','.join(columns)}" if return_obj else "RETURNING id"
		print(q)
		cursor = None
		try:
			cursor = await self._exec(q, vals)
			if type(obj) is list:
				if return_obj:
					return [dict(row) for row in await cursor.fetchall()]
				else:
					return [row[0] for row in await cursor.fetchall()]
			else:
				if return_obj:
					obj_to_return = await cursor.fetchone()
					return dict(obj_to_return)
				return cursor.lastrowid
		except Exception as e:
			raise map_errors(e) from e
		finally:
			if cursor is not None:
				await cursor.close()
	
	async def update(self, id, obj, **filters):
		if type(obj) is list and type(id) is list:
			if not obj:
				return 0
			if self.mapper is not None:
				obj_list = [self.mapper.to_storage_dict(o) for o in obj]
			else:
				obj_list = [o.model_dump() for o in obj]
			columns = obj_list[0].keys()
			vals = [(*obj.values(), i) for i, obj in zip(id, obj_list)]
		else:
			if self.mapper is not None:
				fields_dict = self.mapper.to_storage_dict(obj)
			else:
				fields_dict = obj.model_dump(exclude_unset=True)
			columns = fields_dict.keys()
			vals = list(fields_dict.values())
			vals.append(id)
		if len(columns) == 0:
			return 0
		q = f'UPDATE {self.name} SET '
		q += ', '.join([c + ' = ?' for c in columns])
		q += ' WHERE id = ?'
		cursor = None
		try:
			if type(obj) is list and type(id) is list:
				cursor = await self._exec(q, vals, many=True)
			else:
				cursor = await self._exec(q, vals)
			return cursor.rowcount
		except Exception as e:
			raise map_errors(e) from e
		finally:
			if cursor is not None:
				await cursor.close()

	async def _exec(self, query, params=None, many=False):
		if params is None:
			cursor = await self.db.execute(query)
		else:
			if many:
				print('oo')
				cursor = await self.db.executemany(query, params)
			else:
				cursor = await self.db.execute(query, params)
		return cursor

	
	async def commit(self):
		await self.db.commit()

	async def rollback(self):
		await self.db.rollback()
	
