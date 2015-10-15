drop table if exists client;
create table client (
	id integer primary key autoincrement,
	name text not null,
	imgFilename text,
	industry text
);
drop table if exists clientContact;
create table clientContact (
	id integer primary key autoincrement,
	firstName text not null,
	lastName text not null,
	email text not null,
	phone integer,
	address text not null,
	clientId integer,
	foreign key(clientId) references client(id)
);
drop table if exists clientRequirements;
create table clientRequirements (
	id integer primary key autoincrement,
	RSF integer not null,
	budget integer,
	employees integer,
	market text,
	clientId integer not null,
	foreign key(clientId) references client(id)

);
drop table if exists property;
create table property (
	id integer primary key autoincrement,
	name text not null,
	imagepath text,
	address text not null,
	description text,
	RSF integer not null,
	rent integer not null,
	employees integer,
	market text
);
drop table if exists client_property;
create table client_property (
	id integer primary key autoincrement,
	clientId integer not null,
	propertyId integer not null,
	comment text,
	rating boolean,
	showing boolean not null,
	foreign key(clientId) references client(id),
	foreign key(propertyId) references property(id)
);