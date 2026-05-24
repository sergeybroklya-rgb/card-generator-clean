import streamlit as st
import pandas as pd
import os
import tempfile
from card_generator import process_product
from auth import register_user, login_user, can_generate, increment_generations, save_history, get_history, get_all_users, activate_subscription

st.set_page_config(
    page_title="Генератор карточек товаров",
    page_icon="📦",
    layout="wide"
)

# Инициализация сессии
if 'user' not in st.session_state:
    st.session_state.user = None

# ---------- БОКОВАЯ ПАНЕЛЬ (информация о пользователе) ----------
with st.sidebar:
    if st.session_state.user:
        st.markdown(f"### 👤 {st.session_state.user['email']}")
        
        if st.session_state.user['subscription_active']:
            st.success("✅ Подписка активна")
            if st.session_state.user['subscription_until']:
                st.caption(f"До: {st.session_state.user['subscription_until'][:10]}")
        else:
            remaining = 3 - st.session_state.user['total_generations']
            if remaining > 0:
                st.warning(f"⚠️ Осталось {remaining} бесплатных генераций")
            else:
                st.error("❌ Бесплатные генерации закончились")
                st.info("💳 **Подписка: 3000 ₽/мес**")
                
                # Кнопка со ссылкой на Telegram-бота
                st.markdown("### 📲 Перейдите в нашего Telegram-бота")
                st.markdown("[👉 @SmartCard1_Bot](https://t.me/SmartCard1_Bot)")
                st.caption("После оплаты подписка активируется автоматически")
        
        st.divider()
        st.caption(f"📊 Всего генераций: {st.session_state.user['total_generations']}")
        
        if st.button("🚪 Выйти"):
            st.session_state.user = None
            st.rerun()

# ---------- АДМИН-ПАНЕЛЬ (видна только admin@example.com) ----------
if st.session_state.user and st.session_state.user['email'] == 'admin@example.com':
    with st.sidebar:
        st.divider()
        st.markdown("### 🔧 Админ-панель")
        
        with st.expander("👥 Пользователи"):
            users = get_all_users()
            for user in users:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.caption(f"**{user['email']}**")
                    st.caption(f"Генераций: {user['total_generations']}")
                    if user['subscription_active']:
                        st.caption(f"✅ Подписка до: {user['subscription_until'][:10] if user['subscription_until'] else 'активна'}")
                    else:
                        st.caption("❌ Подписка не активна")
                with col2:
                    if st.button(f"🎁 Активировать", key=f"sub_{user['id']}"):
                        activate_subscription(user['id'], 30)
                        st.success(f"✅ Подписка активирована для {user['email']}")
                        st.rerun()

# ---------- СТРАНИЦА ВХОДА/РЕГИСТРАЦИИ ----------
if not st.session_state.user:
    st.title("📦 Генератор карточек товаров")
    st.markdown("Создавайте SEO-оптимизированные карточки для Wildberries и Ozon за 5 секунд")
    
    tab1, tab2 = st.tabs(["🔐 Вход", "📝 Регистрация"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            submitted = st.form_submit_button("Войти", use_container_width=True)
            
            if submitted:
                user = login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Неверный email или пароль")
    
    with tab2:
        with st.form("register_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            password2 = st.text_input("Повторите пароль", type="password")
            submitted = st.form_submit_button("Зарегистрироваться", use_container_width=True)
            
            if submitted:
                if password != password2:
                    st.error("❌ Пароли не совпадают")
                elif len(password) < 6:
                    st.error("❌ Пароль должен быть не менее 6 символов")
                else:
                    if register_user(email, password):
                        st.success("✅ Регистрация успешна! Теперь войдите")
                    else:
                        st.error("❌ Пользователь с таким email уже существует")

# ---------- ОСНОВНОЙ ИНТЕРФЕЙС (для авторизованных) ----------
else:
    st.title(f"📦 Генератор карточек товаров")
    
    main_tab, history_tab = st.tabs(["🚀 Генерация", "📜 История"])
    
    # ==================== ВКЛАДКА ГЕНЕРАЦИИ ====================
    with main_tab:
        # Проверка, может ли пользователь генерировать
        if not can_generate(st.session_state.user['id']):
            st.error("❌ У вас закончились бесплатные генерации")
            st.info("💳 **Подписка: 3000 ₽/мес**")
            
            # Кнопка со ссылкой на Telegram-бота
            st.markdown("### 📲 Перейдите в нашего Telegram-бота для оплаты")
            st.markdown("[👉 @SmartCard1_Bot](https://t.me/SmartCard1_Bot)")
            st.caption("После оплаты подписка активируется автоматически")
            
            st.stop()
        
        st.markdown("### 📤 Загрузите файл с товарами")
        st.caption("Поддерживаются колонки: `product_name`, `brand`, `category`, `price`, `color`, `features`")
        
        uploaded_file = st.file_uploader("Выберите Excel файл", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                required_cols = ['product_name', 'brand', 'category', 'price']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Отсутствуют колонки: {', '.join(missing_cols)}")
                    with st.expander("📋 Как должен выглядеть файл"):
                        st.dataframe(pd.DataFrame({
                            'product_name': ['Наушники JBL Tune 510BT'],
                            'brand': ['JBL'],
                            'category': ['Аудио'],
                            'price': [3500],
                            'color': ['чёрный'],
                            'features': ['Bluetooth 5.0, 40 часов работы']
                        }))
                else:
                    st.success(f"✅ Загружено {len(df)} товаров")
                    
                    with st.expander("📋 Предпросмотр загруженных данных"):
                        st.dataframe(df.head(10))
                    
                    if st.button("🚀 Сгенерировать карточки", type="primary", use_container_width=True):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        new_cols = ['generated_title', 'generated_description_1', 'generated_description_2',
                                   'generated_description_3', 'generated_keywords', 'generated_specs']
                        for col in new_cols:
                            if col not in df.columns:
                                df[col] = ""
                        
                        total = len(df)
                        for idx, row in df.iterrows():
                            status_text.text(f"🔄 Обработка {idx + 1} из {total}: {row['product_name']}")
                            row_dict = row.to_dict()
                            try:
                                result = process_product(row_dict)
                                for col, value in result.items():
                                    df.at[idx, col] = value
                            except Exception as e:
                                st.warning(f"⚠️ Ошибка при обработке товара {idx + 1}: {e}")
                            progress_bar.progress((idx + 1) / total)
                        
                        status_text.text("✅ Готово!")
                        
                        # Сохраняем результат
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                            df.to_excel(tmp.name, index=False)
                            tmp_path = tmp.name
                        
                        # Увеличиваем счётчик и сохраняем историю
                        increment_generations(st.session_state.user['id'])
                        save_history(st.session_state.user['id'], uploaded_file.name, len(df), tmp_path)
                        
                        # Обновляем данные пользователя в сессии
                        updated_user = login_user(st.session_state.user['email'], "dummy")
                        if updated_user:
                            st.session_state.user = updated_user
                        
                        with open(tmp_path, 'rb') as f:
                            st.download_button(
                                label="📥 Скачать результат (Excel)",
                                data=f,
                                file_name="products_cards.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True
                            )
                        os.unlink(tmp_path)
                        
                        st.balloons()
                        st.success("🎉 Карточки успешно сгенерированы!")
                        
            except Exception as e:
                st.error(f"❌ Ошибка при чтении файла: {e}")
    
    # ==================== ВКЛАДКА ИСТОРИИ ====================
    with history_tab:
        st.subheader("📜 История генераций")
        history = get_history(st.session_state.user['id'])
        
        if history:
            for item in history:
                with st.expander(f"📄 {item['filename']} — {item['products_count']} товаров ({item['created_at'][:16]})"):
                    st.caption(f"Дата: {item['created_at']}")
                    st.caption(f"Товаров: {item['products_count']}")
        else:
            st.info("📭 Пока нет ни одной генерации. Загрузите файл во вкладке «Генерация»")