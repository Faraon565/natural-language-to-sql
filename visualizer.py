import plotly.express as px


def get_auto_chart(df):
    cols = df.columns
    # Если 2 колонки: Категория и Число
    if len(cols) == 2:
        if df[cols[1]].dtype in ['int64', 'float64']:
            return px.bar(df, x=cols[0], y=cols[1], title="Распределение данных")

    # Если есть даты
    for col in cols:
        if 'date' in col.lower():
            return px.line(df, x=col, y=cols[len(cols)-1], title="Динамика во времени")

    return None  # Если график не подходит, оставляем таблицу
