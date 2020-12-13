# Statuses

| Name          | Type          | Description   |
|:------------- |:--------------|:--------------|
id | integer | -
uid | integer | id пользователя из таблицы users
payment | float | необходимая пользователю сумма
sdate | datetime | дата начала статуса
ndays | datetime | количество дней, если статус красный; null, если оранжевый
type | varchar | тип статуса (red/orange)
---
> [Главная](../index.md)
