from __future__ import annotations

import datetime as dt
from typing import Dict, List

import pandas as pd
import pydeck as pdk
import streamlit as st


def _render_metric_cards(metrics: List[Dict[str, str]]) -> None:
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        col.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{metric['label']}</div>
                <div class="metric-value">{metric['value']}</div>
                <div class="metric-trend">{metric['trend']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_styles() -> None:
    st.markdown(
        """
        <style>
        .metric-card {
            background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%);
            padding: 18px 20px;
            border-radius: 16px;
            color: #ffffff;
            box-shadow: 0 12px 24px rgba(31, 64, 55, 0.35);
            margin-bottom: 16px;
        }
        .metric-label {
            font-size: 0.85rem;
            opacity: 0.85;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 6px;
        }
        .metric-trend {
            font-size: 0.8rem;
            margin-top: 8px;
            opacity: 0.85;
        }
        .notification-card {
            background: rgba(255, 255, 255, 0.7);
            border-radius: 12px;
            padding: 14px 18px;
            border: 1px solid rgba(31, 64, 55, 0.2);
            margin-bottom: 12px;
        }
        .notification-card strong {
            color: #1f4037;
        }
        .pasture-badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            background: rgba(31, 64, 55, 0.1);
            color: #1f4037;
            font-size: 0.75rem;
            margin-left: 8px;
        }
        .section-card {
            background: rgba(255, 255, 255, 0.75);
            padding: 18px 20px;
            border-radius: 16px;
            border: 1px solid rgba(31, 64, 55, 0.12);
            box-shadow: 0 10px 22px rgba(31, 64, 55, 0.12);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_smart_pasture() -> None:
    """Render the Smart Pasture cockpit experience."""
    _render_styles()

    st.title("🐮 智慧牛场驾驶舱")
    st.caption(
        "实时掌握牛群动态、位置分布与健康状态，一键将精准坐标推送给牧场主，打造数字化养殖体验。"
    )

    metrics = [
        {"label": "牛只总数", "value": "128 头", "trend": "较上周新增 5 头犊牛"},
        {"label": "正在放牧", "value": "93 头", "trend": "草场覆盖率 86%"},
        {"label": "休息/反刍", "value": "21 头", "trend": "平均反刍 6.5 小时/日"},
        {"label": "定位告警", "value": "2 条", "trend": "低电量项圈待更换"},
    ]
    _render_metric_cards(metrics)

    herd_positions = [
        {
            "tag_id": "CN-001",
            "name": "雪莲",
            "latitude": 43.8562,
            "longitude": 125.3284,
            "activity": "悠闲放牧",
            "pasture": "西北草场",
            "last_update": "5 分钟前",
        },
        {
            "tag_id": "CN-014",
            "name": "赤霞",
            "latitude": 43.8615,
            "longitude": 125.3368,
            "activity": "向河谷移动",
            "pasture": "清泉牧道",
            "last_update": "8 分钟前",
        },
        {
            "tag_id": "CN-027",
            "name": "琥珀",
            "latitude": 43.8528,
            "longitude": 125.3411,
            "activity": "低速行进",
            "pasture": "南坡草甸",
            "last_update": "12 分钟前",
        },
        {
            "tag_id": "CN-045",
            "name": "云舒",
            "latitude": 43.8583,
            "longitude": 125.3204,
            "activity": "静卧休憩",
            "pasture": "桦林遮蔽带",
            "last_update": "3 分钟前",
        },
        {
            "tag_id": "CN-063",
            "name": "灵溪",
            "latitude": 43.8649,
            "longitude": 125.3322,
            "activity": "沿水渠行走",
            "pasture": "北岸补饲区",
            "last_update": "6 分钟前",
        },
        {
            "tag_id": "CN-088",
            "name": "晨光",
            "latitude": 43.8484,
            "longitude": 125.3299,
            "activity": "群聚觅食",
            "pasture": "南部开阔地",
            "last_update": "14 分钟前",
        },
    ]
    herd_df = pd.DataFrame(herd_positions)

    st.subheader("牛群位置实时分布")
    st.markdown(
        "通过高精度北斗项圈持续追踪每一头牛的位置，并实时汇总到驾驶舱地图。"
    )

    deck = pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-streets-v12",
        initial_view_state=pdk.ViewState(
            latitude=herd_df["latitude"].mean(),
            longitude=herd_df["longitude"].mean(),
            zoom=13,
            pitch=45,
        ),
        tooltip={
            "html": "<strong>{name}</strong><br/>编号：{tag_id}<br/>位置：{pasture}<br/>状态：{activity}",
            "style": {"backgroundColor": "#1f4037", "color": "white"},
        },
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=herd_df,
                get_position="[longitude, latitude]",
                get_radius=65,
                get_fill_color="[255, 170, 28, 200]",
                pickable=True,
            )
        ],
    )
    st.pydeck_chart(deck)

    display_df = herd_df[[
        "tag_id",
        "name",
        "pasture",
        "activity",
        "last_update",
    ]].rename(
        columns={
            "tag_id": "电子耳标",
            "name": "牛只名称",
            "pasture": "所在草场",
            "activity": "当前动态",
            "last_update": "最新更新时间",
        }
    )
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    col_left, col_right = st.columns((2, 1))
    with col_left:
        st.markdown("### 草场巡检播报")
        st.markdown(
            """
            <div class="section-card">
                <p>· 西北草场牧草覆盖良好，需注意 14 号清泉牧道低洼处积水。</p>
                <p>· 北岸补饲区新增 2 台智能饮水槽，水质监测正常。</p>
                <p>· 桦林遮蔽带风速 6m/s，建议傍晚引导牛群向南坡草甸休息。</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_right:
        st.markdown("### 环境健康指数")
        env_data = pd.DataFrame(
            {
                "时间": [
                    (dt.datetime.now() - dt.timedelta(hours=hours)).strftime("%H:%M")
                    for hours in range(6, -1, -1)
                ],
                "舒适度": [82, 84, 83, 81, 85, 86, 87],
            }
        )
        st.line_chart(env_data.set_index("时间"), color="#1f4037")

    st.markdown("---")
    st.subheader("向牧场主发送实时位置通知")
    st.markdown("一键生成定位说明，将牛群的最新位置与附加提醒推送给牧场主。")

    st.session_state.setdefault("pasture_notifications", [])

    with st.form("notify_owner"):
        selected_cow = st.selectbox(
            "选择牛只",
            options=herd_positions,
            format_func=lambda cow: f"{cow['name']}（{cow['tag_id']}）",
        )
        default_message = (
            f"{selected_cow['name']} 当前位于 {selected_cow['pasture']}，状态：{selected_cow['activity']}。"
        )
        st.markdown(f"**位置概述：** {default_message}")
        additional_note = st.text_area(
            "附加说明",
            value=f"建议安排巡检员在 {selected_cow['pasture']} 周边确认围栏情况。",
            height=80,
        )
        submitted = st.form_submit_button("发送位置通知", use_container_width=True)

        if submitted:
            notification = {
                "timestamp": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "cow": f"{selected_cow['name']}（{selected_cow['tag_id']}）",
                "location": selected_cow["pasture"],
                "status": selected_cow["activity"],
                "message": f"{default_message} {additional_note.strip()}",
            }
            st.session_state["pasture_notifications"].append(notification)
            st.success(
                f"已将 {selected_cow['name']} 的最新位置推送给牧场主，稍后可在通知记录中查看详情。"
            )

    if st.session_state["pasture_notifications"]:
        st.markdown("#### 通知发送记录")
        for item in reversed(st.session_state["pasture_notifications"][-5:]):
            st.markdown(
                f"""
                <div class="notification-card">
                    <strong>{item['timestamp']}</strong> · {item['cow']}<span class="pasture-badge">{item['location']}</span><br/>
                    <em>状态：{item['status']}</em><br/>
                    {item['message']}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("暂无通知记录，选择牛只并填写说明后即可推送位置。")

    st.markdown("---")
    st.markdown(
        """
        #### 草场分区速览
        - **西北草场**：丘陵缓坡，适合白天放牧，覆盖 36 头牛。
        - **清泉牧道**：沿溪流分布，傍晚引导牛群回栏的主要通道。
        - **南坡草甸**：夜间休息区，设有红外相机监测掩护情况。
        - **北岸补饲区**：集中补饲和防疫站点，可实时查看饲喂计划执行情况。
        """
    )
