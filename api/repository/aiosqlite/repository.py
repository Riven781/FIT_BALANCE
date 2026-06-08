from typing import Annotated

import aiosqlite
from fastapi import Depends

from api.database.db import get_db
from api.repository.aiosqlite.errors_mapper import map_errors


class DbRepository:
	def __init__(self, db : aiosqlite.Connection, name=''):
		self.db = db
		self.name = name

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
	
	async def delete(self, id):
		q = f'DELETE FROM {self.name} WHERE id = ?'
		cursor = None
		try:
			cursor = await self._exec(q, [id])
			return cursor.rowcount
		except Exception as e:
			raise map_errors(e) from e
		finally:
			if cursor is not None:
				await cursor.close()

	async def insert(self, obj):
		fields_dict = obj.model_dump()
		columns = fields_dict.keys()
		vals = list(fields_dict.values())
		print(vals)
		q = f'INSERT INTO {self.name} (' + ', '.join(columns) + ') VALUES ('
		q += ', '.join(['?' for v in vals]) + ')'
		cursor = None
		try:
			cursor = await self._exec(q, vals)
			return cursor.lastrowid
		except Exception as e:
			raise map_errors(e) from e
		finally:
			if cursor is not None:
				await cursor.close()
	
	async def update(self, id, obj):
		fields_dict = obj.model_dump(exclude_unset=True)
		columns = fields_dict.keys()
		vals = list(fields_dict.values())
		if len(columns) == 0:
			return 0
		q = f'UPDATE {self.name} SET '
		q += ', '.join([c + ' = ?' for c in columns])
		q += ' WHERE id = ' + str(id)
		cursor = None
		try:
			cursor = await self._exec(q, vals)
			return cursor.rowcount
		except Exception as e:
			raise map_errors(e) from e
		finally:
			if cursor is not None:
				await cursor.close()

	async def _exec(self, query, params=None):
		if params is None:
			cursor = await self.db.execute(query)
		else:
			cursor = await self.db.execute(query, params)
		return cursor

	
	async def commit(self):
		await self.db.commit()

	async def rollback(self):
		await self.db.rollback()
	
