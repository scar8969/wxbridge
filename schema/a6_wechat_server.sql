-- 💬 wechat-server schema
CREATE TABLE contacts(id INTEGER PRIMARY KEY, wxid TEXT UNIQUE, name TEXT, is_group INTEGER DEFAULT 0, created_at DATETIME);
CREATE TABLE messages(id INTEGER PRIMARY KEY, contact_id INTEGER REFERENCES contacts(id), direction TEXT DEFAULT 'in', text TEXT, at DATETIME);
CREATE TABLE rules(id INTEGER PRIMARY KEY, trigger TEXT, action TEXT DEFAULT 'reply', params_json TEXT DEFAULT '{}', enabled INTEGER DEFAULT 1);
