# orange_status
NEW_ORANGE_STATUS = 200
APPROVE_ORANGE_STATUS = 210
DECLINE_ORANGE_STATUS = 220

# red status
NEW_RED_STATUS = 300
APPROVE_RED_STATUS = 310
DECLINE_RED_STATUS = 320

# intention
INTENTION_APPROVED = 1
INTENTION_DECLINE = 0

# obligations
NEW_OBLIGATION = 410
OBLIGATION_APPROVED = 420
OBLIGATION_DECLINE = 430

#
MONEY_HAS_BEEN_SENT = 500
REMIND_LATER = 600

# closed
CLOSED = 0xff

# Коды первой версии

# Статусы, пока что не доконца продуманные
# 0 - отменённое намерение
# 1 - созданное намерение
# 10 - отменённое обязательство
# 11 - созданное обязательство (намерение переведено в обязательство)
# 12 - деньги на обязательство отправлены, но не подтверждены получателем
# 13 - деньги подтверждены отправка и получение
# 15 - запрос получателя на исполнение (дай денег)
