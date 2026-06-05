from typing import Annotated

import aiosqlite
from fastapi import Depends

from api.database.db import get_db


class DbRepository:
	def __init__(self, db : aiosqlite.Connection):
		self.db = db

	async def select(self, table_name, filters_dict={}, all=False):
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
	
	async def delete(self, table_name, id):
		q = f'DELETE FROM {table_name} WHERE id = ?'
		cursor = await self.exec(q, [id])
		try:
			return cursor.rowcount
		finally:
			await cursor.close()

	async def insert(self, table_name, colnames, vals):
		q = f'INSERT INTO {table_name} (' + ', '.join(colnames) + ') VALUES ('
		q += ', '.join(['?' for v in vals]) + ')'
		cursor = await self.exec(q, vals)
		try:
			return cursor.lastrowid
		finally:
			await cursor.close()
	
	async def update(self, table_name, id, colnames, vals):
		if len(colnames) == 0:
			return 0
		q = f'UPDATE {table_name} SET '
		q += ', '.join([c + ' = ?' for c in colnames])
		q += ' WHERE id = ' + str(id)
		cursor = await self.exec(q, vals)
		try:
			return cursor.rowcount
		finally:
			await cursor.close()

	async def exec(self, query, params=None):
		if params is None:
			cursor = await self.db.execute(query)
		else:
			cursor = await self.db.execute(query, params)
		return cursor

	
	async def commit(self):
		await self.db.commit()

	async def rollback(self):
		await self.db.rollback()
	
