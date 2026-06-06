from typing import Annotated

import aiosqlite
from fastapi import Depends

from api.database.db import get_db


class DbRepository:
	def __init__(self, db : aiosqlite.Connection, name=''):
		self.db = db
		self.name = name

	async def _select(self, table_name, filters_dict={}, all=False):
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

		async with self.db.execute(query, values) as cursor:
			if all == True:
				rows = await cursor.fetchall()
			else:
				rows = await cursor.fetchone()
			await cursor.close()
		return rows
	
	async def delete(self, id):
		q = f'DELETE FROM {self.name} WHERE id = ?'
		cursor = await self._exec(q, [id])
		try:
			return cursor.rowcount
		finally:
			await cursor.close()

	async def insert(self, obj):
		fields_dict = obj.model_dump()
		columns = fields_dict.keys()
		vals = list(fields_dict.values())
		print(vals)
		q = f'INSERT INTO {self.name} (' + ', '.join(columns) + ') VALUES ('
		q += ', '.join(['?' for v in vals]) + ')'
		cursor = await self._exec(q, vals)
		try:
			return cursor.lastrowid
		finally:
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
		cursor = await self._exec(q, vals)
		try:
			return cursor.rowcount
		finally:
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
	
