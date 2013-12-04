#!/usr/local/bin/python

import os
import re
import sqlite3

# init/clear db
resBase = os.path.join('vorbis.docset', 'Contents', 'Resources')
db = sqlite3.connect(os.path.join(resBase, 'docSet.dsidx'))
cur = db.cursor()
try:
	cur.execute('DROP TABLE searchIndex;')
except:
	pass
cur.execute('CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
# add libs
docBase = os.path.join(resBase, 'Documents')
libs = 'libogg', 'libvorbis', 'vorbisenc', 'vorbisfile'
getInfo = re.compile(r'^<h1>(?P<name>.+?)</h1>').search
for lib in libs:
	relDocPath = os.path.join(lib, 'index.html')
	name = lib
	cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Library', relDocPath))
	print('lib: %s' % name)
# add structs/functions
getInfo = re.compile(r'^<a href="(?P<path>.+?\.html)">(?P<name>.+?)</a><br>').search
for lib in libs:
	with open(os.path.join(docBase, lib, 'reference.html')) as page:
		for line in page:
			info = getInfo(line)
			if info:
				info = info.groupdict()
				name, path = info['name'], info['path']
				if path.startswith('../'):
					continue
				path = os.path.join(lib, path)
				if name.endswith('()'):
					name = name[:-2]
					type = 'Function'
				else:
					type = 'Struct'
				cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, type, path))
				print('name: %s, path: %s, type: %s' % (name, path, type))
# add return code defines
getInfo = re.compile(r'^<dt>(?P<name>.+?)</dt>').search
relDocPath = os.path.join('libvorbis', 'return.html')
with open(os.path.join(docBase, relDocPath)) as page:
	for line in page:
		info = getInfo(line)
		if info:
			name = info.groupdict()['name']
			cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, 'Define', relDocPath))
			print('ret code: %s' % name)
# close db
db.commit()
db.close()
