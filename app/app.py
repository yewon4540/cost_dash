import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
from dash.dcc import send_file

# 데이터 읽기
df = pd.read_csv('./data.csv')

# 제품 키워드와 매칭되는 값 정의
keyword_mapping = {
    'Amazon Elastic Compute Cloud': '서버',
    'Data Transfer': '데이터 이동',
    'Amazon Simple Storage Service': '스토리지',
    'Amazon Virtual Private Cloud': '네트워크',
    '총계': '총계'
}

# df['제품'] 값을 키워드에 따라 변환
df['제품'] = df['제품'].map(lambda x: keyword_mapping.get(x, x))
df['제품'] = df['제품'].fillna('총계')

# 총계 제거하기
try:
    df.drop('총계 (￦)', axis=1, inplace=True)
except:
    pass

# 날짜 열 추출
date_columns = df.columns[2:-1]

# 비용 데이터에서 쉼표(,) 제거 후 숫자형으로 변환
for col in date_columns:
    df[col] = df[col].replace({',': ''}, regex=True).astype(float)

# 날짜 형식을 'YYYY-MM-DD'와 'MM월 DD일'로 변환
formatted_dates_full = [
    pd.to_datetime(date, format="%m/%d/%Y").strftime('%Y-%m-%d') for date in date_columns
]
formatted_dates_display = [
    pd.to_datetime(date, format="%m/%d/%Y").strftime('%m월 %d일') for date in date_columns
]

# 데이터 변환 (melt 처리 및 날짜 변환 적용)
df_melted = df.melt(id_vars=["제품"], value_vars=date_columns, var_name="날짜", value_name="비용")
df_melted["날짜_YYYYMMDD"] = pd.to_datetime(df_melted["날짜"], format="%m/%d/%Y").dt.strftime('%Y-%m-%d')
df_melted["날짜_MM월DD일"] = pd.to_datetime(df_melted["날짜"], format="%m/%d/%Y").dt.strftime('%m월 %d일')

# 비용 데이터가 문자열로 읽히는 경우 숫자형으로 변환
df_melted["비용"] = pd.to_numeric(df_melted["비용"], errors='coerce').fillna(0)

# Dash 애플리케이션 초기화
app = dash.Dash(__name__)

# 레이아웃 설정
app.layout = html.Div([
    html.H1("학생관리시스템 요금", style={'text-align': 'center'}),
    html.Div(
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=formatted_dates_full[0],  # 시작 날짜
            end_date=formatted_dates_full[-1],  # 종료 날짜
            display_format='YYYY-MM-DD',  # 표시 형식
            start_date_placeholder_text="날짜 선택",  # 플레이스홀더
            minimum_nights=0,  # 날짜 범위 최소 선택일
        ),
        style={'text-align': 'center', 'margin-bottom': '20px'}  # 가운데 정렬
    ),
    dcc.Graph(id='bar-chart'),
    html.Div(
        children=[
            dcc.Checklist(
                id='product-checklist',
                options = [{'label': product, 'value': product} for product in df['제품'].dropna().unique()],
                value=['총계'],  # 기본값: '총계'만 선택
                inline=True
            )
        ],
        style={
            'display': 'flex',
            'justify-content': 'center',  # 좌우 중앙 정렬
            'align-items': 'center',  # 상하 중앙 정렬
            'margin-top': '20px',  # 그래프와의 간격 조정
        }
    ),
    html.Div(
        children=[
            dash_table.DataTable(
                id='data-table',
                style_table={
                    'margin-left': '0',  # 완전히 좌측 정렬
                    'width': '100%',
                    'overflowY': 'scroll',  # 세로 스크롤바 추가
                    'maxHeight': '400px',  # 표 최대 높이 설정
                    'border': '1px solid #ddd',  # 테두리 추가
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'left'  # 헤더 좌측 정렬
                },
                style_data={
                    'whiteSpace': 'normal',
                    'height': 'auto',
                    'textAlign': 'left'  # 데이터 좌측 정렬
                }
            )
        ]
    ),
    html.Div(
    html.Button(
        "엑셀 파일 다운로드", 
        id="download-btn", 
        style={
            'margin-top': '20px',
            'font-size': '18px',  # 글자 크기
            'padding': '10px 20px',  # 버튼 내부 여백
            'width': '200px',  # 버튼 너비
            'height': '50px',  # 버튼 높이
            'background-color': 'rgb(102, 197, 204)',  # 버튼 배경색
            'color': 'white',  # 글자 색
            'border': 'none',  # 테두리 제거
            'border-radius': '5px',  # 버튼 모서리 둥글게
            'cursor': 'pointer'  # 커서를 손가락 모양으로 변경
        }
    ),
    style={
        'display': 'flex',
        'justify-content': 'center',  # 가로 중앙 정렬
        'align-items': 'center',  # 세로 중앙 정렬
    }
),

    dcc.Download(id="download-dataframe-xlsx")
])

# 콜백 설정
# Dash 콜백 수정
@app.callback(
    [Output('bar-chart', 'figure'),
     Output('data-table', 'columns'),
     Output('data-table', 'data')],
    Input('product-checklist', 'value'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')
)
def update_graph_and_table(selected_products, start_date, end_date):
    # 선택된 날짜 범위 필터링
    if not start_date or not end_date:
        # 날짜가 선택되지 않았을 경우 빈 데이터를 반환
        return {}, [], []

    filtered_df = df_melted[
        (df_melted['제품'].isin(selected_products)) &
        (df_melted['날짜_YYYYMMDD'] >= start_date) &
        (df_melted['날짜_YYYYMMDD'] <= end_date)
    ]
    
    if filtered_df.empty:
        # 필터링된 데이터가 없을 경우 빈 데이터를 반환
        return {}, [], []

    # 막대그래프 생성
    fig = px.bar(
        filtered_df,
        x="날짜_MM월DD일",
        y="비용",
        color="제품",
        barmode="group",
        title="제품별 요금 현황",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(
        xaxis_title="날짜",
        yaxis_title="비용 ($)",
        legend_title="제품",
        title_font_size=20,
        legend_title_font_size=14,
        legend_font_size=12,
        template="plotly_white"
    )

    # 데이터를 피벗하여 표 형식으로 변환
    pivot_table = filtered_df.pivot(index="제품", columns="날짜_MM월DD일", values="비용").fillna(0)
    pivot_table['총계'] = pivot_table.sum(axis=1).round(2)  # 각 행의 총합 계산 및 소숫점 2자리로 반올림
    pivot_table.reset_index(inplace=True)  # 인덱스를 컬럼으로 변환

    # 표의 컬럼과 데이터 구성
    columns = [{"name": col, "id": col} for col in pivot_table.columns]
    data = pivot_table.to_dict('records')

    return fig, columns, data

# 엑셀 다운로드 콜백
@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("download-btn", "n_clicks"),
    prevent_initial_call=True
)
def download_table(n_clicks):
    # 다운로드용 데이터 생성
    path = "/tmp/filtered_data.xlsx"
    filtered_table = pd.DataFrame(dash.callback_context.outputs_list[1]["data"])
    filtered_table.to_excel(path, index=False)
    return send_file(path)

# 애플리케이션 실행
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=5000)
