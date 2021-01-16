# Описание возможностей и функций, реализованных в MVP-боте
В боте взаимной помощи реализуются три основных типа действий пользователя:
- профиль пользователя – позволяет выбирать статус и указывать основные данные, необходимые для включения в круг и оказания прямой адресной помощи;
- действия по оказанию помощи - от запроса помощи до подтверждения исполнения обязательства;
- проявление сети участников, связанных общими кругами заботы, возможность просматривать участников своего круга и расширять свой круг за счет помощи другим участникам.

## Действия пользователя

### Заполнение профиля
- [Задание и смена статуса](actions/change_status.md)
- [Информация о пользователе](actions/change_chat_link.md)
- [Задание и смена реквизитов](actions/change_requisites.md)
- [Изменение языка](actions/change_language.md)
- [Удалиться из бота](actions/delete_from_bot.md)

### Действия в органайзере
**В пользу других участников сети**
- [Просмотр и управление своими  намерениями и обязательствами](actions/show_int_obl.md)
- [Создание намерения](actions/create_intent.md)
- [Коррекция, отмена или исполнение намерения](actions/correction_my_intention.md)
- [Перевод намерения в обязательство](actions/creation_of_obligation.md)
- [Исполнение обязательства](actions/money_transfer.md)

**В свою пользу**
- [Просмотр и управление намерениями и обязательствами в свою пользу](actions/show_int_obl_for_me.md)
- [Просьба о переводе намерения в обязательство](actions/request_for_transfer.md)
- [Хранение или отмена обязательства](actions/save_obligation.md)
- [Запрос на исполнение обязательства](actions/request_for_execution.md)

**Архив обязательств**
- [Архив исполненных обязательств](actions/archive_my.md)
- [Архив не исполненных вовремя обязательств](actions/archive.md)

### Действия в главном меню
- [Просмотр участников и расширение своего круга](actions/show_circle.md)
- [Список участников, которым помогает пользователь](actions/list_my_people.md)
- [Список участников, которые помогают пользователю](actions/list_other_people.md)
- [Создание ссылки-приглашения о помощи себе или нуждающимся участникам своей сети](actions/create_invite.md)
- [Напоминание или подтверждение исполнения обязательства](actions/confirmation_of_transfer.md)

- [Получение справки о работе бота](actions/faq.md)
- [Чат поддержки](actions/support_chat.md)


### Оповещения
- [О смене статуса пользователя в круге](notifications/status_changed.md)
- [О создании намерения в сторону пользователя](notifications/intention_created.md)
- [Просьба о переводе намерения в обязательство](notifications/request_for_translation.md)
- [Уведомление о переводе намерения в обязательство](notifications/obligation_created.md)
- [Просьба подтвердить исполнение обязательства](notifications/reminder_of_obligation.md)
- [Уведомление об исполнении обязательства](notifications/money_transferred.md)
- [Напоминание о необходимости подтвердить исполнение обязательства](notifications/reminder_to_confirm.md)
- [Уведомление о подтверждении исполнения обязательства получателем](notifications/money_received.md)
- [Уведомление о завершении экстренного сбора](notifications/end_red.md)


### Таблицы базы данных
- [users](tables/users.md)
- [events](tables/events.md)
- [statuses](tables/statuses.md)
- [intentions](tables/intentions.md)
- [requisites](tables/requisites.md)
- [circle](tables/circle.md)


### FAQ
- [Про бота](faq/about_bot.md)
- [Как начать пользоваться](faq/how_start.md)
- [Условные обозначения](faq/conventions.md)
- [Описание меню](faq/menu.md)
- [Возможные кейсы](faq/cases.md)
