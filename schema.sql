drop table if exists client;
create table client (
	id integer primary key autoincrement,
	name text not null,
	imgFilename text,
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
drop table if exists property;
create table property (
	id integer primary key autoincrement,
	name text not null,
	imagepath text,
	address text not null,
	description text
);
drop table if exists client_property;
create table client_property (
	clientId integer not null,
	propertyId integer not null,
	comment text,
	rating boolean,
	showing boolean not null,
	foreign key(clientId) references client(id),
	foreign key(propertyId) references property(id)
);