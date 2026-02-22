# Сводка по новым автотестам API

## Обзор

В рамках расширения тестового покрытия API Smart Pack Production созданы следующие тестовые модули:

---

## E2E Тесты (`tests/e2e/`)

### 1. `test_warehouse_lifecycle.py`
**Сценарий:** Полный цикл жизни роликов на складе  
**Покрывает UI Cases:** 5-10 (Склад - загрузка, слияние, архивация)

| Тест | Описание |
|------|----------|
| `test_01_load_roll_first` | Загрузка первого ролика |
| `test_02_load_roll_second` | Загрузка второго ролика |
| `test_03_get_info_before_merge` | Получение информации перед слиянием |
| `test_04_merge_rolls` | Слияние двух роликов |
| `test_05_change_exp_date` | Изменение срока годности |
| `test_06_archive_roll` | Архивация ролика (в архив) |
| `test_07_get_archived_rolls` | Проверка фильтрации архивных |
| `test_08_unarchive_roll` | Возврат ролика из архива на склад |
| `test_09_verify_roll_on_warehouse` | Проверка отображения на складе после возврата |

**Endpoints:**
- `POST /api/web/v1/warehouse/load`
- `POST /api/web/v1/warehouse/get_info_before_merge`
- `POST /api/web/v1/warehouse/merge_rolls`
- `POST /api/web/v1/warehouse/change_exp_date`
- `POST /api/web/v1/warehouse/is_archived/change`
- `POST /api/web/v1/warehouse/filter`

---

### 2. `test_barcode_operations.py`
**Сценарий:** Генерация штрихкодов и этикеток  
**Покрывает UI Cases:** 55 (Генерация агрегационных стикеров)

| Тест | Описание |
|------|----------|
| `test_01_generate_barcodes_by_codes` | Генерация PDF по списку кодов |
| `test_02_generate_barcodes_by_gtin` | Генерация PDF по GTIN |
| `test_03_generate_barcodes_to_file` | Сохранение файла штрихкодов |
| `test_04_filter_generated_barcodes` | Фильтрация сгенерированных |

**Endpoints:**
- `POST /api/web/v1/barcodes/generate_by_codes`
- `POST /api/web/v1/barcodes/generate_by_gtin`
- `POST /api/web/v1/barcodes/generate_to_file`
- `POST /api/web/v1/barcodes/generated/filter`

---

### 3. `test_serialization_advanced.py`
**Сценарий:** Расширенная функциональность сериализации  
**Покрывает UI Cases:** 15-26 (Переменный вес, диапазоны, брак, отмены)

| Тест | Описание |
|------|----------|
| `test_01_start_shift_with_variable_weight` | Запуск с переменным весом |
| `test_02_add_code_with_weight` | Добавление КМ с весом |
| `test_03_fill_aggregate_mode` | Режим "Агрегат" |
| `test_04_range_add_start_code` | Начало диапазона |
| `test_05_range_add_finish_code` | Окончание диапазона |
| `test_06_cancel_start_code` | Отмена начального кода |
| `test_07_defect_single_code` | Брак поштучно |
| `test_08_defect_range` | Брак по диапазону |
| `test_09_cancel_code_by_roll` | Отмена по ролику |
| `test_10_cancel_range` | Отмена диапазона |
| `test_11_finish_shift` | Завершение смены |
| `test_12_resume_shift` | Возобновление партии |
| `test_13_finish_shift_again` | Повторное завершение |

**Endpoints:**
- `POST /api/web/v1/work_shift/start`
- `POST /api/web/v1/work_shift/add_code`
- `POST /api/web/v1/work_shift/add_roll`
- `POST /api/web/v1/work_shift/range/add_start_code`
- `POST /api/web/v1/work_shift/range/add_finish_code`
- `POST /api/web/v1/work_shift/range/cancel_start_code`
- `POST /api/web/v1/work_shift/defect/add`
- `POST /api/web/v1/work_shift/defect/add_range`
- `POST /api/web/v1/work_shift/cancel/codes_by_roll`
- `POST /api/web/v1/work_shift/cancel/codes_range`
- `POST /api/web/v1/work_shift/finish`
- `POST /api/web/v1/work_shift/resume`

---

### 4. `test_aggregation_advanced.py`
**Сценарий:** Расширенная функциональность агрегации  
**Покрывает UI Cases:** 31-38, 47-53 (Пресеты, паллеты, ТЗ, расформирование)

| Тест | Описание |
|------|----------|
| `test_01_create_and_save_preset` | Создание пресета |
| `test_02_filter_presets` | Фильтрация пресетов |
| `test_03_start_session_with_preset` | Запуск с пресетом |
| `test_04_add_codes_to_session` | Добавление КМ |
| `test_05_add_package` | Добавление упаковки |
| `test_06_add_pallet` | Добавление палеты |
| `test_07_add_package_to_pallet` | Упаковка в палету |
| `test_08_close_pallet` | Закрытие палеты |
| `test_09_vision_mode_add_codes` | Техническое зрение |
| `test_10_package_info` | Информация об упаковке |
| `test_11_withdrawal_code` | Изъятие кода |
| `test_12_disband_package` | Расформирование |
| `test_13_finish_session` | Завершение сессии |
| `test_14_delete_preset` | Удаление пресета |

**Endpoints:**
- `POST /api/web/v1/aggregation_session/preset/add`
- `POST /api/web/v1/aggregation_session/preset/filter`
- `POST /api/web/v1/aggregation_session/start`
- `POST /api/web/v1/aggregation_session/add_code`
- `POST /api/web/v1/aggregation_session/add_package`
- `POST /api/web/v1/aggregation_session/add_pallet`
- `POST /api/web/v1/aggregation_session/add_code_to_package`
- `POST /api/web/v1/aggregation_session/close_pallet`
- `POST /api/web/v1/aggregation_session/vision/add_codes`
- `POST /api/web/v1/aggregation_session/package_info`
- `POST /api/web/v1/aggregation_session/withdrawal_code`
- `POST /api/web/v1/aggregation_session/disbandment_package`
- `POST /api/web/v1/aggregation_session/finish`
- `POST /api/web/v1/aggregation_session/preset/delete`

---

### 5. `test_reports_advanced.py`
**Сценарий:** Продвинутая работа с отчетами  
**Покрывает UI Cases:** 56-63 (Повторная отправка, ручной статус, CSV)

| Тест | Описание |
|------|----------|
| `test_01_send_utilisation_report` | Отчет о нанесении |
| `test_02_send_aggregation_report` | Отчет об агрегации |
| `test_03_filter_reports` | Фильтрация отчетов |
| `test_04_resend_failed_report` | Повторная отправка |
| `test_05_set_manual_status` | Ручной статус |
| `test_06_download_report_csv` | Скачивание CSV |
| `test_07_download_aggregation_csv` | CSV агрегации |
| `test_08_report_statistics` | Статистика отчетов |
| `test_09_download_excel` | Выгрузка Excel |
| `test_10_gis_check_code` | Проверка в ГИС |

**Endpoints:**
- `POST /api/web/v1/report/send_utilisation`
- `POST /api/web/v1/report/send_aggregation`
- `POST /api/web/v1/report/filter`
- `POST /api/web/v1/report/resend`
- `POST /api/web/v1/report/set_report_status`
- `POST /api/web/v1/report/download`
- `POST /api/web/v1/report/aggregation/download`
- `POST /api/web/v1/report/statistics`
- `POST /api/web/v1/report/download_excel`
- `POST /api/web/v1/report/gis/check_code`

---

### 6. `test_aggregation_session_close_scenarios.py`
**Сценарий:** Закрытие сессий с неполными упаковками/палетами  
**Покрывает UI Cases:** 41-46

| Тест | Case | Описание |
|------|------|----------|
| `test_41_close_partial_package_full_pallet_print_line` | 41 | Неполная упаковка + Полная палета (печать на линии) |
| `test_42_close_partial_package_full_pallet_pre_printed` | 42 | Неполная упаковка + Полная палета (преднанесенный) |
| `test_43_close_full_package_partial_pallet_print_line` | 43 | Полная упаковка + Неполная палета (печать на линии) |
| `test_44_close_full_package_partial_pallet_pre_printed` | 44 | Полная упаковка + Неполная палета (преднанесенный) |
| `test_45_close_partial_package_partial_pallet_print_line` | 45 | Неполная упаковка + Неполная палета (печать на линии) |
| `test_46_close_partial_package_partial_pallet_pre_printed` | 46 | Неполная упаковка + Неполная палета (преднанесенный) |
| `test_close_with_pin_code` | 40-46 | Закрытие с вводом пин-кода |

**Endpoints:**
- `POST /api/web/v1/aggregation_session/start`
- `POST /api/web/v1/aggregation_session/add_code`
- `POST /api/web/v1/aggregation_session/add_package`
- `POST /api/web/v1/aggregation_session/add_pallet`
- `POST /api/web/v1/aggregation_session/close_pallet`
- `POST /api/web/v1/aggregation_session/finish`

**Особенности реализации:**
- Двойное подтверждение при неполных контейнерах
- Различие логики для "печать на линии" и "преднанесенный стикер"
- Обработка пин-кодов
- Печать SSCC при закрытии

---

### 7. `test_code_verification.py`
**Сценарий:** Проверка кода маркировки (Case 64)  
**Покрывает UI Case 64:** Доступ к разделу "Проверить код"

| Тест | Описание |
|------|----------|
| `test_01_verify_valid_code_in_gis` | Проверка валидного КМ в ГИС МТ |
| `test_02_verify_code_not_found` | Несуществующий код в ГИС |
| `test_03_verify_code_withdrawn` | Выбывший код (списан) |
| `test_04_verify_code_in_warehouse` | Код на складе (в ролике) |
| `test_05_verify_code_in_aggregation` | Код в агрегате (упаковка/палета) |
| `test_06_verify_code_in_work_shift` | Код в производственной партии |
| `test_07_verify_invalid_code_format` | Невалидный формат кода |
| `test_08_verify_code_without_gtin` | Неполный код (без GTIN) |

**Endpoints:**
- `POST /api/web/v1/check_gis_code` — Проверка в ГИС МТ
- `POST /api/web/v1/warehouse/get_roll_by_code` — Поиск на складе
- `POST /api/web/v1/aggregation_session/check_code` — Проверка в агрегации
- `POST /api/web/v1/work_shift/find_work_shift_by_code` — Поиск в партиях

**Особенности реализации:**
- Комплексная проверка кода во всех системах (ГИС, склад, агрегация, партии)
- Различные статусы кода: в обороте, выбыл, агрегирован, на складе
- Валидация формата кода маркировки

---

## Интеграционные Тесты (`tests/integration/`)

### 6. `test_gtin_management.py`
**Сценарий:** Управление реестром GTIN  
**Покрывает UI Cases:** Реестр GTIN

| Тест | Описание |
|------|----------|
| `test_add_gtin_positive` | Добавление GTIN |
| `test_filter_gtin` | Поиск GTIN |
| `test_edit_gtin_positive` | Редактирование GTIN |
| `test_update_gtin_registry_data` | Обновление реестра |
| `test_change_update_flag` | Изменение флага обновления |

**Endpoints:**
- `POST /api/web/v1/gtin/add_many`
- `POST /api/web/v1/gtin/filter`
- `POST /api/web/v1/gtin/edit`
- `POST /api/web/v1/gtin/update_data_gtin`
- `POST /api/web/v1/gtin/change_flag_update_gtin_registry`

---

### 7. `test_notifications.py`
**Сценарий:** Управление уведомлениями  
**Покрывает UI Cases:** Настройки уведомлений

| Тест | Описание |
|------|----------|
| `test_get_flags_and_recipients` | Получение настроек |
| `test_add_recipient_positive` | Добавление получателя |
| `test_set_flags_for_notification` | Настройка флагов |
| `test_delete_recipient_positive` | Удаление получателя |

**Endpoints:**
- `GET /api/web/v1/notification/get_flags_and_recipients`
- `POST /api/web/v1/notification/add_recipient`
- `POST /api/web/v1/notification/set_flags_for_notification`
- `POST /api/web/v1/notification/delete_recipient`

---

### 8. `test_user_management.py`
**Сценарий:** Управление пользователями  
**Покрывает UI Cases:** 68-72 (Личный кабинет, пользователи)

| Тест | Описание |
|------|----------|
| `test_get_current_user` | Текущий пользователь |
| `test_filter_users` | Фильтрация пользователей |
| `test_user_change_password` | Смена пароля |
| `test_edit_user_info` | Редактирование данных |
| `test_get_user_permissions` | Права пользователя |
| `test_update_user_permissions` | Обновление прав |
| `test_create_new_user` | Создание пользователя |
| `test_deactivate_activate_user` | Блокировка/разблокировка |
| `test_get_owner_profile` | Профиль владельца |

**Endpoints:**
- `GET /api/web/v1/user/me`
- `POST /api/web/v1/user/filter`
- `POST /api/web/v1/user/password/change`
- `POST /api/web/v1/user/edit`
- `POST /api/web/v1/user/permissions/get`
- `POST /api/web/v1/user/permissions/update`
- `POST /api/web/v1/user/create`
- `POST /api/web/v1/user/deactivate`
- `POST /api/web/v1/user/activate`
- `GET /api/web/v1/get_owner_profile`

---

### 9. `test_aggregation.py`
**Сценарий:** Дополнительные операции агрегации  
**Покрывает UI Cases:** 28, 37-38, 47-53

| Тест | Описание |
|------|----------|
| `test_filter_aggregation_sessions` | Фильтрация сессий |
| `test_get_active_session` | Активная сессия |
| `test_get_session_detail_info` | Детальная информация |
| `test_get_session_hierarchy` | Иерархия сессии |
| `test_get_hierarchy_detail` | Детальная иерархия |
| `test_check_code_in_session` | Проверка кода |
| `test_buffer_kity_statistics` | Статистика KITY |
| `test_buffer_kigu_statistics` | Статистика KIGU |
| `test_buffer_kin_statistics` | Статистика KIN |
| `test_preset_filter` | Фильтрация пресетов |
| `test_dashboard_filter` | Фильтрация дашбордов |

**Endpoints:**
- `POST /api/web/v1/aggregation_session/filter`
- `POST /api/web/v1/aggregation_session/active`
- `POST /api/web/v1/aggregation_session/get_detail_info`
- `POST /api/web/v1/aggregation_session/hierarchy`
- `POST /api/web/v1/aggregation_session/hierarchy/detail`
- `POST /api/web/v1/aggregation_session/check_code`
- `POST /api/web/v1/aggregation_session/buffer/kity/statistics`
- `POST /api/web/v1/aggregation_session/buffer/kigu/statistics`
- `POST /api/web/v1/aggregation_session/buffer/kin/statistics`
- `POST /api/web/v1/aggregation_session/preset/filter`
- `POST /api/web/v1/aggregation_session/dashboard/filter`

---

### 10. `test_feedback.py`
**Сценарий:** Обратная связь  
**Покрывает UI Cases:** 67 (Предложения и пожелания)

| Тест | Описание |
|------|----------|
| `test_send_feedback_positive` | Отправка обратной связи |
| `test_send_feedback_bug_report` | Отчет об ошибке |
| `test_send_feedback_negative_empty_message` | Валидация пустого сообщения |

**Endpoints:**
- `POST /api/web/v1/feedback/send`

---

### 11. Дополнения к `test_warehouse.py`
**Добавленные тесты:**

| Тест | Описание |
|------|----------|
| `test_filter_rolls_archived` | Архивные ролики |
| `test_get_roll_by_code` | Поиск по КМ |
| `test_count_codes_in_roll` | Подсчет кодов |
| `test_get_roll_info` | Информация о ролике |
| `test_get_used_in_work_shift` | История использования |
| `test_get_last_code` | Последний код |
| `test_download_warehouse_codes` | Скачивание кодов |
| `test_map_get_metadata` | Метаданные карты |
| `test_map_get_detail_metadata` | Детальные метаданные |

---

## Итоговая статистика покрытия

### По разделам UI документации:

| Раздел | Cases | Покрытие |
|--------|-------|----------|
| Авторизация | 1-2 | ✅ Базовые тесты |
| Заказы | 3-4 | ✅ Базовые тесты |
| Склад | 5-10 | ✅ Полное покрытие |
| Сериализация | 11-27 | ✅ Полное покрытие |
| Агрегация | 28-55 | ✅ Полное покрытие |
| Отчеты | 56-63 | ✅ Полное покрытие |
| Проверить код | 64 | ✅ Полное покрытие |
| Партнеры | 65 | ⚠️ Не покрыто |
| Change log | 66 | ⚠️ Не покрыто |
| Предложения | 67 | ✅ Покрыто |
| Личный кабинет | 68-72 | ✅ Полное покрытие |
| Поддержка | 73-75 | ⚠️ Частично |

### Новые endpoints в покрытии:

- **Warehouse:** 8 новых endpoints
- **Barcodes:** 4 новых endpoints  
- **Work Shift (advanced):** 12 новых endpoints
- **Aggregation (advanced):** 14 новых endpoints
- **Reports (advanced):** 10 новых endpoints
- **GTIN:** 5 новых endpoints
- **Notifications:** 4 новых endpoints
- **User Management:** 9 новых endpoints
- **Feedback:** 1 новый endpoint

**Всего новых тестовых файлов:** 12  
**Всего новых тест-кейсов:** 100+
