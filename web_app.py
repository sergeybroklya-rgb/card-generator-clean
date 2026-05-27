import streamlit as st
import pandas as pd
import io
import os
import tempfile
from card_generator import process_product
from auth import register_user, login_user, can_generate, increment_generations, save_history, get_history, get_all_users, activate_subscription

# ==================== НАСТРОЙКИ ====================
st.set_page_config(
    page_title="Генератор карточек товаров",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== ДИЗАЙН ====================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b1120 0%, #1a1a2e 100%);
    }
    body, .stApp, .stMarkdown, p, div, span, label {
        color: #ffffff !important;
    }
    h1 {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    .subheader {
        text-align: center;
        font-size: 1.2rem;
        color: #a0aec0 !important;
        margin-bottom: 2rem;
    }
    .stExpander, [data-testid="stForm"], .stTabs [data-baseweb="tab-list"] {
        background: #1e293b !important;
        border-radius: 20px !important;
        border: 1px solid #334155 !important;
        padding: 1.2rem !important;
        margin-bottom: 1rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1e293b !important;
        border-radius: 30px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        border: 1px solid #334155 !important;
    }
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
        border-color: #3b82f6 !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 40px !important;
        padding: 0.6rem 1.5rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
        width: 100%;
        font-size: 1rem !important;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59,130,246,0.4);
    }
    .stTextInput input, .stTextInput textarea {
        background: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 0.6rem 1rem !important;
    }
    .stTextInput label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
        margin-bottom: 0.3rem !important;
    }
    .success-box {
        background: #064e3b;
        border-left: 5px solid #10b981;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: white;
    }
    .error-box {
        background: #7f1d1d;
        border-left: 5px solid #ef4444;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        color: white;
    }
    .stProgress > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
        border-radius: 20px;
    }
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    .step {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.8rem;
        padding: 0.6rem;
        border-radius: 12px;
        background: #0f172a;
    }
    .step-number {
        background: #3b82f6;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        color: white;
    }
    hr {
        border-color: #334155;
        margin: 1.5rem 0;
    }
    .stRadio > div {
        gap: 1rem;
    }
    .stRadio label {
        background: #0f172a !important;
        padding: 0.5rem 1rem !important;
        border-radius: 30px !important;
        border: 1px solid #334155 !important;
    }
    .stRadio [role="radiogroup"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== ШАПКА ====================
st.markdown("""
<div style="max-width: 1200px; margin: 0 auto; text-align: center;">
    <h1>📦 Генератор карточек товаров</h1>
    <div style="font-size: 1.1rem; color: #a0aec0; margin-bottom: 2rem;">
        Создавайте SEO-оптимизированные карточки для Wildberries, Ozon и Яндекс Маркет за 5 секунд
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== СЕССИЯ ====================
if 'user' not in st.session_state:
    st.session_state.user = None

# ==================== ФУНКЦИЯ ШАБЛОНА ====================
def get_template_download():
    template_df = pd.DataFrame({
        'product_name': ['Наушники JBL Tune 510BT'],
        'brand': ['JBL'],
        'category': ['Аудио'],
        'price': [3500],
        'color': ['чёрный'],
        'features': ['Bluetooth 5.0, 40 часов работы']
    })
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False)
    return output.getvalue()

# ==================== БОКОВАЯ ПАНЕЛЬ ====================
with st.sidebar:
    st.markdown("### 🧙‍♂️ Аккаунт")
    if st.session_state.user:
        st.markdown(f"**👤 {st.session_state.user['email']}**")
        if st.session_state.user.get('subscription_active', False):
            st.success("✅ Подписка активна")
        else:
            remaining = 3 - st.session_state.user.get('total_generations', 0)
            if remaining > 0:
                st.warning(f"⚠️ Осталось {remaining} бесплатных генераций")
            else:
                st.error("❌ Генерации закончились")
                st.info("💳 Подписка: 3000 ₽/мес")
                st.markdown("[👉 Купить подписку](https://t.me/SmartCard1_Bot)")
        st.divider()
        st.caption(f"📊 Всего генераций: {st.session_state.user.get('total_generations', 0)}")
        if st.button("🚪 Выйти", use_container_width=True):
            st.session_state.user = None
            st.rerun()
    else:
        st.info("🔐 Войдите или зарегистрируйтесь")
        st.caption("После входа откроется генератор")

# ==================== ОСНОВНОЙ КОНТЕНТ ====================
if not st.session_state.user:
    tab1, tab2 = st.tabs(["🔐 Вход", "📝 Регистрация"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="user@example.com")
            password = st.text_input("Пароль", type="password", placeholder="••••••••")
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
            email = st.text_input("Email", placeholder="user@example.com")
            password = st.text_input("Пароль", type="password", placeholder="минимум 6 символов")
            password2 = st.text_input("Повторите пароль", type="password", placeholder="••••••••")
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

else:
    main_tab, history_tab = st.tabs(["🚀 Генерация", "📜 История"])
    
    with main_tab:
        with st.expander("📖 Как пользоваться", expanded=False):
            st.markdown("""
            <div class="step">
                <div class="step-number">1</div>
                <div><strong>Скачайте шаблон Excel</strong> — нажмите кнопку ниже</div>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <div><strong>Заполните колонки</strong> данными ваших товаров</div>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <div><strong>Загрузите файл</strong> в сервис</div>
            </div>
            <div class="step">
                <div class="step-number">4</div>
                <div><strong>Выберите тон описания</strong></div>
            </div>
            <div class="step">
                <div class="step-number">5</div>
                <div><strong>Выберите маркетплейс</strong> (Wildberries / Ozon / Яндекс Маркет)</div>
            </div>
            <div class="step">
                <div class="step-number">6</div>
                <div><strong>Нажмите «Сгенерировать»</strong> — получите готовые карточки</div>
            </div>
            <div class="step">
                <div class="step-number">7</div>
                <div><strong>Скачайте результат</strong> и опубликуйте</div>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.download_button(
                label="📥 Скачать шаблон",
                data=get_template_download(),
                file_name="template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.caption("Нажмите, чтобы скачать шаблон Excel")
        
        with st.expander("📋 Пример заполненной таблицы", expanded=False):
            example_df = pd.DataFrame({
                'product_name': ['Наушники JBL Tune 510BT', 'Смартфон Xiaomi Redmi Note 12'],
                'brand': ['JBL', 'Xiaomi'],
                'category': ['Аудио', 'Смартфоны'],
                'price': [3500, 25000],
                'color': ['чёрный', 'синий'],
                'features': ['Bluetooth 5.0, 40 ч работы', '6.67", 128 ГБ, камера 50 МП']
            })
            st.dataframe(example_df, use_container_width=True)
            st.caption("📌 Обязательные колонки: product_name, brand, category, price")
            st.caption("📌 Необязательные: color, features")
        
        st.divider()
        
        remaining = 3 - st.session_state.user.get('total_generations', 0)
        if remaining <= 0 and not st.session_state.user.get('subscription_active', False):
            st.error("❌ У вас закончились бесплатные генерации")
            st.info("💳 **Подписка: 3000 ₽/мес** — напишите @SmartCard1_Bot")
            st.stop()
        
        # ВЫБОР ТОНА
        st.markdown("### 🎭 Выберите тон описания")
        tone = st.radio(
            "Как должен звучать текст?",
            options=["professional", "friendly", "selling"],
            format_func=lambda x: {
                "professional": "📝 Профессиональный (сухо, факты)",
                "friendly": "😊 Дружелюбный (тёплый, вежливый)",
                "selling": "🔥 Продающий (эмоциональный, яркий)"
            }[x],
            horizontal=True
        )
        
        # ВЫБОР МАРКЕТПЛЕЙСА (БЕЗ ПЕРЕВОДА)
        st.markdown("### 🏪 Выберите маркетплейс")
        marketplace = st.radio(
            "Для какой площадки нужна карточка?",
            options=["WB", "Ozon", "Yandex"],
            format_func=lambda x: {
                "WB": "📦 Wildberries",
                "Ozon": "🛒 Ozon",
                "Yandex": "🔍 Яндекс Маркет"
            }[x],
            horizontal=True,
            help="Оптимизируем описание под правила выбранного маркетплейса"
        )
        
        # Преобразуем для передачи в process_product
        marketplace_map = {
            "WB": "wildberries",
            "Ozon": "ozon",
            "Yandex": "yandex"
        }
        marketplace_value = marketplace_map[marketplace]
        
        st.divider()
        
        uploaded_file = st.file_uploader("📁 Загрузите Excel файл", type=['xlsx', 'xls'])
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                required_cols = ['product_name', 'brand', 'category', 'price']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Отсутствуют колонки: {', '.join(missing_cols)}")
                else:
                    st.success(f"✅ Загружено {len(df)} товаров")
                    
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
                            status_text.text(f"🔄 {idx+1}/{total}: {row['product_name']}")
                            row_dict = row.to_dict()
                            try:
                                result = process_product(row_dict, tone=tone, marketplace=marketplace_value)
                                for col, value in result.items():
                                    df.at[idx, col] = value
                            except Exception as e:
                                st.warning(f"⚠️ Ошибка: {e}")
                            progress_bar.progress((idx+1)/total)
                        
                        status_text.text("✅ Готово!")
                        
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df.to_excel(writer, index=False)
                        
                        increment_generations(st.session_state.user['id'])
                        save_history(st.session_state.user['id'], uploaded_file.name, len(df), "")
                        
                        updated = login_user(st.session_state.user['email'], "dummy")
                        if updated:
                            st.session_state.user = updated
                        
                        st.download_button(
                            label="📥 Скачать результат",
                            data=output.getvalue(),
                            file_name="products_cards.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                        st.balloons()
                        st.success("🎉 Карточки успешно сгенерированы!")
                        
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")
    
    with history_tab:
        st.subheader("📜 История")
        history = get_history(st.session_state.user['id'])
        if history:
            for item in history:
                with st.expander(f"📄 {item['filename']} — {item['products_count']} товаров ({item['created_at'][:16]})"):
                    st.caption(f"📅 {item['created_at']}")
        else:
            st.info("📭 Нет генераций")