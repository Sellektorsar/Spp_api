# Детальный анализ тестового покрытия по тест-кейсам

**Дата анализа:** 20.02.2026  
**Всего тест-кейсов:** 75

---

## Сводная таблица покрытия

| № | Тест-кейс | Раздел | Покрытие | Файл(ы) тестов | Комментарий |
|---|-----------|--------|----------|----------------|-------------|
| 1 | Авторизация в системе | Настройки | ✅ ПОЛНОЕ | `tests/integration/test_auth.py` | test_login_success, test_login_invalid_credentials, test_login_missing_fields |
| 2 | Проверка роли и опций | Настройки | ⚠️ ЧАСТИЧНОЕ | `tests/e2e/test_user_management.py` | Есть тест прав, но нет проверки таблицы грантов |
| 3 | Доступ к разделу "Заказы" | Заказы | ✅ ПОЛНОЕ | `tests/integration/test_orders.py`, `tests/e2e/test_order_lifecycle.py` | Фильтрация, статусы, выгрузка |
| 4 | Создание заказа | Заказы | ✅ ПОЛНОЕ | `tests/integration/test_orders.py` | TestOrderCreation - создание ЦСКД/СУЗ |
| 5 | Доступ к разделу "Склад" | Склад | ✅ ПОЛНОЕ | `tests/integration/test_warehouse.py`, `tests/e2e/test_warehouse_operations.py` | Фильтрация, кнопки, вкладки |
| 6 | Добавление/удаление ролика | Склад | ✅ ПОЛНОЕ | `tests/e2e/test_warehouse_operations.py` | test_01_load_first_roll_positive, test_21_cleanup_test_rolls |
| 7 | Поиск ролика по КМ | Склад | ✅ ПОЛНОЕ | `tests/integration/test_warehouse.py` | test_get_roll_by_code |
| 8 | Объединение роликов | Склад | ✅ ПОЛНОЕ | `tests/e2e/test_warehouse_operations.py` | test_10_get_info_before_merge, test_11_merge_rolls_positive |
| 9 | Автоматическое перемещение в Архив | Склад | ⚠️ ЧАСТИЧНОЕ | `tests/integration/test_warehouse.py` | test_filter_rolls_archived - только проверка архива, нет теста авто-перемещения |
| 10 | Ручное перемещение в Архив | Склад | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** перемещения со Склада в Архив и обратно |
| 11 | Доступ к разделу "Сериализация" | Сериализация | ✅ ПОЛНОЕ | `tests/integration/test_work_shift.py` | Фильтрация смен, активные/неактивные линии |
| 12 | Создание производственной линии | Сериализация | ✅ ПОЛНОЕ | `tests/integration/test_line_management.py`, `tests/e2e/test_line_management.py` | Создание, название, ТГ |
| 13 | Удаление производственной линии | Сериализация | ✅ ПОЛНОЕ | `tests/integration/test_line_management.py`, `tests/e2e/test_line_management.py` | Удаление, восстановление |
| 14 | Создание партии | Сериализация | ✅ ПОЛНОЕ | `tests/integration/test_work_shift.py` | test_start_shift_milk |
| 15 | Переменный вес/фактический объем | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_01_start_shift_with_variable_weight, test_02_add_code_with_weight |
| 16 | Несколько GTIN в партии (УЗ) | Сериализация | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** - только для УЗ |
| 17 | Наполнение партии "Агрегат" | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_03_fill_aggregate_mode |
| 18 | Наполнение партии "Диапазон" | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_04_range_add_start_code, test_05_range_add_finish_code, test_06_cancel_start_code |
| 19 | Наполнение партии "Штучно" | Сериализация | ✅ ПОЛНОЕ | `tests/integration/test_work_shift.py`, `tests/e2e/test_order_lifecycle.py` | test_add_code_to_created_shift |
| 20 | Редактирование партии "Агрегат" | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_09_cancel_code_by_roll |
| 21 | Редактирование партии "Диапазон" | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_10_cancel_range |
| 22 | Редактирование партии "Штучно" | Сериализация | ⚠️ ЧАСТИЧНОЕ | `tests/e2e/test_serialization_advanced.py` | Есть отмена, но нет отдельного редактирования штучно |
| 23 | Удаление брака "Диапазон" | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_08_defect_range |
| 24 | Удаление брака "Штучно" | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_07_defect_single_code |
| 25 | Закрытие партии | Сериализация | ✅ ПОЛНОЕ | `tests/integration/test_work_shift.py`, `tests/e2e/test_serialization_advanced.py` | С пин-кодом и без |
| 26 | Возобновление партии | Сериализация | ✅ ПОЛНОЕ | `tests/e2e/test_serialization_advanced.py` | test_12_resume_shift |
| 27 | Отправка отчетов по партии | Сериализация | ✅ ПОЛНОЕ | `tests/integration/test_reports.py`, `tests/e2e/test_reports_advanced.py` | Разные страны, ТГ |
| 28 | Доступ к разделу "Агрегация" | Агрегация | ✅ ПОЛНОЕ | `tests/integration/test_aggregation_session.py` | Фильтрация сессий, вкладки |
| 29 | Создание агрегационной линии | Агрегация | ✅ ПОЛНОЕ | `tests/integration/test_line_management.py` | Создание линии агрегации |
| 30 | Удаление агрегационной линии | Агрегация | ✅ ПОЛНОЕ | `tests/integration/test_line_management.py` | Удаление, восстановление |
| 31 | Запуск сессии "Агрегация КМ" | Агрегация | ✅ ПОЛНОЕ | `tests/integration/test_aggregation_session.py` | test_start_pallets_session |
| 32 | Сохранение пресета | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_01_create_and_save_preset |
| 33 | Использование пресета | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_03_start_session_with_preset |
| 34 | Удаление пресета | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_14_delete_preset |
| 35 | Наполнение сессии "2D сканер печать на линии" | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_04_add_codes_to_session |
| 36 | Наполнение сессии "Преднанесенный стикер" | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_42_close_partial_package_full_pallet_pre_printed |
| 37 | Наполнение сессии "Техническое зрение" преднанесенный | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_09_vision_mode_add_codes |
| 38 | Наполнение сессии "Техническое зрение" печать | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_09_vision_mode_add_codes |
| 39 | Закрытие пустой сессии | Агрегация | ⚠️ ЧАСТИЧНОЕ | `tests/integration/test_aggregation_session.py` | Есть finish, но нет явной проверки пустой сессии |
| 40 | Закрытие сессии с полной упаковкой/палетой | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_close_with_pin_code |
| 41 | Неполная упаковка + полная палета (печать) | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_41_close_partial_package_full_pallet_print_line |
| 42 | Неполная упаковка + полная палета (стикер) | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_42_close_partial_package_full_pallet_pre_printed |
| 43 | Полная упаковка + неполная палета (печать) | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_43_close_full_package_partial_pallet_print_line |
| 44 | Полная упаковка + неполная палета (стикер) | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_44_close_full_package_partial_pallet_pre_printed |
| 45 | Неполная упаковка + неполная палета (печать) | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_45_close_partial_package_partial_pallet_print_line |
| 46 | Неполная упаковка + неполная палета (стикер) | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_session_close_scenarios.py` | test_46_close_partial_package_partial_pallet_pre_printed |
| 47 | Запуск сессии "Паллетная агрегация" | Агрегация | ✅ ПОЛНОЕ | `tests/integration/test_aggregation_session.py` | test_start_pallets_session |
| 48 | Наполнение сессии "Паллетная агрегация" | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_06_add_pallet, test_07_add_package_to_pallet |
| 49 | Закрытие сессии "Паллетная агрегация" | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_08_close_pallet, test_13_finish_session |
| 50 | Отправка отчетов по сессии | Агрегация | ✅ ПОЛНОЕ | `tests/integration/test_reports.py`, `tests/e2e/test_reports_advanced.py` | send_aggregation, send_atk |
| 51 | Поиск по КМ или агрегату | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_10_package_info |
| 52 | Редактирование агрегата | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_11_withdrawal_code |
| 53 | Расформирование агрегата | Агрегация | ✅ ПОЛНОЕ | `tests/e2e/test_aggregation_advanced.py` | test_12_disband_package |
| 54 | Повторная печать стикера | Агрегация | ⚠️ ЧАСТИЧНОЕ | `tests/e2e/test_printer_integration.py` | Есть печать, но нет явного теста повторной печати стикера агрегата |
| 55 | Генерация агрегационных стикеров | Агрегация | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** генерации преднанесенных стикеров |
| 56 | Доступ к разделу "Отчеты" | Отчеты | ✅ ПОЛНОЕ | `tests/integration/test_reports.py` | test_filter_reports_default, пагинация, фильтры |
| 57 | Подписание отчета | Отчеты | ⚠️ ЧАСТИЧНОЕ | `tests/integration/test_reports.py` | Нет теста с цифровой подписью |
| 58 | Отклонение отчета | Отчеты | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** отклонения отчета |
| 59 | Удаление выбывших КМ | Отчеты | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** удаления выбывших КМ |
| 60 | Повторная отправка отчета | Отчеты | ✅ ПОЛНОЕ | `tests/integration/test_reports.py`, `tests/e2e/test_reports_advanced.py` | test_resend_error_report |
| 61 | Ручной статус отчета | Отчеты | ✅ ПОЛНОЕ | `tests/integration/test_reports.py`, `tests/e2e/test_reports_advanced.py` | test_set_report_status_to_sent |
| 62 | Скачать отчет в CSV | Отчеты | ✅ ПОЛНОЕ | `tests/e2e/test_reports_advanced.py` | test_06_download_report_csv |
| 63 | Выгрузка статистики | Отчеты | ✅ ПОЛНОЕ | `tests/integration/test_reports.py`, `tests/e2e/test_reports_advanced.py` | test_report_statistics |
| 64 | Доступ к разделу "Проверить код" | Проверить код | ⚠️ ЧАСТИЧНОЕ | `tests/e2e/test_reports_advanced.py` | test_10_gis_check_code - есть проверка ГИС, но нет отдельного раздела |
| 65 | Доступ к разделу "Партнеры" | Партнеры | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** работы с партнерами |
| 66 | Доступ к разделу "Change log" | Change log | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** |
| 67 | Доступ к разделу "Предложения и пожелания" | Предложения | ✅ ПОЛНОЕ | `tests/integration/test_feedback.py` | test_send_feedback_positive |
| 68 | Доступ к личному кабинету | Личный кабинет | ✅ ПОЛНОЕ | `tests/integration/test_user_management.py` | test_get_current_user, test_get_owner_profile |
| 69 | Смена пароля | Личный кабинет | ✅ ПОЛНОЕ | `tests/integration/test_user_management.py`, `tests/e2e/test_user_management.py` | test_user_change_password, test_10_update_user_password |
| 70 | Редактирование данных пользователя | Личный кабинет | ✅ ПОЛНОЕ | `tests/integration/test_user_management.py`, `tests/e2e/test_user_management.py` | test_edit_user_info, test_09_edit_user_information |
| 71 | Создание нового пользователя | Личный кабинет | ✅ ПОЛНОЕ | `tests/integration/test_user_management.py`, `tests/e2e/test_user_management.py` | test_create_new_user, test_02_create_user_positive |
| 72 | Блокировка/разблокировка пользователя | Личный кабинет | ✅ ПОЛНОЕ | `tests/integration/test_user_management.py`, `tests/e2e/test_user_management.py` | test_deactivate_activate_user |
| 73 | Доступ к API | Настройки | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** доступа к документации API |
| 74 | Выгрузка инструкции | Настройки | ❌ ОТСУТСТВУЕТ | - | **НЕТ ТЕСТА** скачивания инструкции |
| 75 | Доступ к разделу "Поддержка" | Поддержка | ⚠️ ЧАСТИЧНОЕ | `tests/integration/test_feedback.py` | Есть обратная связь, но нет проверки раздела Поддержка |

---

## Статистика покрытия

| Статус | Количество | Процент |
|--------|------------|---------|
| ✅ ПОЛНОЕ | 55 | 73.3% |
| ⚠️ ЧАСТИЧНОЕ | 10 | 13.3% |
| ❌ ОТСУТСТВУЕТ | 10 | 13.3% |

---

## Детальный анализ по разделам

### 1. Настройки (тест-кейсы 1-2, 73-74)
- **Покрытие:** 2/4 полных, 1 частичный, 1 отсутствует
- **Проблемы:**
  - Нет проверки таблицы грантов для ролей (Case 2)
  - Нет теста доступа к API документации (Case 73)
  - Нет теста скачивания инструкции (Case 74)

### 2. Заказы (тест-кейсы 3-4)
- **Покрытие:** 2/2 полных
- **Файлы:** `tests/integration/test_orders.py`, `tests/e2e/test_order_lifecycle.py`

### 3. Склад (тест-кейсы 5-10)
- **Покрытие:** 4/6 полных, 1 частичный, 1 отсутствует
- **Проблемы:**
  - Нет теста автоматического перемещения просроченных роликов (Case 9)
  - Нет теста ручного перемещения в Архив и обратно (Case 10)

### 4. Сериализация (тест-кейсы 11-27)
- **Покрытие:** 15/17 полных, 1 частичный, 1 отсутствует
- **Проблемы:**
  - Нет теста ввода нескольких GTIN для УЗ (Case 16)
  - Редактирование "Штучно" покрыто частично (Case 22)

### 5. Агрегация (тест-кейсы 28-55)
- **Покрытие:** 24/28 полных, 2 частичных, 2 отсутствуют
- **Проблемы:**
  - Нет теста закрытия пустой сессии (Case 39 - частично)
  - Нет теста повторной печати стикера агрегата (Case 54 - частично)
  - Нет теста генерации преднанесенных стикеров (Case 55)

### 6. Отчеты (тест-кейсы 56-63)
- **Покрытие:** 5/8 полных, 1 частичный, 2 отсутствуют
- **Проблемы:**
  - Нет теста подписания с цифровой подписью (Case 57)
  - Нет теста отклонения отчета (Case 58)
  - Нет теста удаления выбывших КМ (Case 59)

### 7. Проверить код (тест-кейс 64)
- **Покрытие:** Частичное
- **Проблема:** Нет отдельного теста раздела "Проверить код"

### 8. Партнеры (тест-кейс 65)
- **Покрытие:** Отсутствует
- **Проблема:** Нет тестов работы с партнерами

### 9. Change log (тест-кейс 66)
- **Покрытие:** Отсутствует
- **Проблема:** Нет тестов

### 10. Предложения и пожелания (тест-кейс 67)
- **Покрытие:** Полное
- **Файлы:** `tests/integration/test_feedback.py`

### 11. Личный кабинет (тест-кейсы 68-72)
- **Покрытие:** 5/5 полных
- **Файлы:** `tests/integration/test_user_management.py`, `tests/e2e/test_user_management.py`

### 12. Поддержка (тест-кейс 75)
- **Покрытие:** Частичное
- **Проблема:** Нет проверки раздела "Поддержка" с FAQ и контактами

---

## Приоритетные недостающие тесты

### Высокий приоритет:
1. **Case 10** - Ручное перемещение роликов в Архив и из Архива
2. **Case 58** - Отклонение отчета
3. **Case 59** - Удаление выбывших КМ из отчета
4. **Case 65** - Работа с партнерами
5. **Case 55** - Генерация агрегационных стикеров

### Средний приоритет:
6. **Case 9** - Автоматическое перемещение в Архив
7. **Case 16** - Несколько GTIN в партии (УЗ)
8. **Case 57** - Подписание отчета с УКЭП
9. **Case 2** - Проверка таблицы грантов
10. **Case 64** - Раздел "Проверить код"

### Низкий приоритет:
11. **Case 66** - Change log
12. **Case 73** - Доступ к API
13. **Case 74** - Выгрузка инструкции
14. **Case 75** - Раздел "Поддержка"

---

## Рекомендации

1. **Добавить интеграционные тесты** для работы с Архивом на складе
2. **Добавить E2E тесты** для работы с партнерами
3. **Добавить тесты** для работы с УКЭП (если применимо)
4. **Расширить тесты отчетов** - добавить отклонение и удаление выбывших КМ
5. **Добавить тесты** для специфичных режимов УЗ (Case 16)

---

## Существующие тестовые файлы

### Integration тесты:
- `test_auth.py` - Авторизация
- `test_orders.py` - Заказы
- `test_warehouse.py` - Склад
- `test_line_management.py` - Управление линиями
- `test_aggregation_session.py` - Сессии агрегации
- `test_reports.py` - Отчеты
- `test_work_shift.py` - Рабочие смены
- `test_user_management.py` - Пользователи
- `test_feedback.py` - Обратная связь
- `test_aggregation.py` - Агрегация
- `test_chain.py` - Цепочки операций
- `test_devices_and_printers.py` - Устройства и принтеры
- `test_gtin_management.py` - Управление GTIN
- `test_gtin_and_line.py` - GTIN и линии
- `test_notifications.py` - Уведомления

### E2E тесты:
- `test_order_lifecycle.py` - Жизненный цикл заказа
- `test_aggregation_session_close_scenarios.py` - Сценарии закрытия агрегации
- `test_user_management.py` - Управление пользователями
- `test_warehouse_operations.py` - Операции склада
- `test_warehouse_lifecycle.py` - Жизненный цикл склада
- `test_serialization_advanced.py` - Расширенная сериализация
- `test_aggregation_advanced.py` - Расширенная агрегация
- `test_reports_advanced.py` - Расширенные отчеты
- `test_line_management.py` - Управление линиями
- `test_printer_integration.py` - Интеграция с принтерами
- `test_barcode_operations.py` - Операции с штрихкодами
- `test_bulk_operations.py` - Массовые операции
- `test_defect_handling.py` - Обработка брака
- `test_gis_integration.py` - Интеграция с ГИС
- `test_integration_with_1c.py` - Интеграция с 1С
- `test_process_interruption.py` - Прерывание процессов
- `test_production_cycle.py` - Производственный цикл
- `test_shipment_process.py` - Процесс отгрузки
- `test_aggregation_cycle.py` - Цикл агрегации
- `test_report_workflow.py` - Рабочий процесс отчетов