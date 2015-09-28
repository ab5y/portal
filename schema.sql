drop table if exists client;
create table client (
	id integer primary key autoincrement,
	name text not null,
	industry text
);
drop table if exists clientContact;
create table clientContact (
	firstName text not null,
	lastName text not null,
	email text not null,
	phone integer,
	address text not null,
	clientId integer,
	foreign key(clientId) references client(id)
);