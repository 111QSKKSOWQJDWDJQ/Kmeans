"""
AI 视频剧本拆解多模态实验室
"""

import streamlit as st
import json
import os

# ============================================================================
# 页面配置
# ============================================================================
st.set_page_config(
    layout="wide",
    page_title="视频剧本拆解实验室",
    page_icon="🎬",
    initial_sidebar_state="expanded",
)

# ============================================================================
# 常量
# ============================================================================
VIDEO_DIR = None  # 部署版不含视频文件
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


# ============================================================================
# Session State
# ============================================================================
def init_state():
    for key, default in [
        ("results", None),
        ("outline_idx", 0),
        ("detail_idx", 0),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default


# ============================================================================
# 辅助函数
# ============================================================================
def fmt(seconds):
    if not seconds:
        return "00:00"
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def load_results(group_id, project="tpn01"):
    path = os.path.join(RESULTS_DIR, f"group{group_id}_{project}_result.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def scan_projects():
    if not os.path.isdir(RESULTS_DIR):
        return {}
    import re
    projects = {}
    for fname in os.listdir(RESULTS_DIR):
        m = re.match(r'group(\d+)_(.+)_result\.json$', fname)
        if m:
            projects.setdefault(m.group(2), []).append(int(m.group(1)))
    for k in projects:
        projects[k] = sorted(projects[k])
    return projects


# ============================================================================
# CSS
# ============================================================================
def inject_css():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Helvetica Neue', sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    /* 减少顶部空白 */
    .block-container {
        padding-top: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 100%;
    }

    /* 隐藏 deploy 按钮和顶部装饰 */
    .stDeployButton, header[data-testid="stHeader"] { display: none !important; }

    /* 侧边栏强制展开 */
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        transform: none !important;
        position: relative !important;
        visibility: visible !important;
    }
    section[data-testid="stSidebar"] > div { visibility: visible !important; }

    /* 顶栏 */
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.8rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid #e8e8ed;
    }
    .top-bar-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1d1d1f;
        letter-spacing: -0.01em;
    }
    .top-bar-sub {
        font-size: 0.8rem;
        color: #86868b;
        margin-left: 0.6rem;
    }

    /* 列标题 */
    .col-title {
        font-size: 0.7rem;
        font-weight: 600;
        color: #86868b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.4rem;
    }

    /* 按钮样式 */
    div[data-testid="stVerticalBlock"] button {
        width: 100%;
        text-align: left !important;
        justify-content: flex-start !important;
        border-radius: 8px !important;
        border: 1px solid #d2d2d7 !important;
        background: #ffffff !important;
        color: #1d1d1f !important;
        font-size: 0.78rem !important;
        font-weight: 400 !important;
        padding: 0.5rem 0.7rem !important;
        line-height: 1.4 !important;
        transition: all 0.12s ease !important;
        box-shadow: none !important;
        white-space: pre-wrap !important;
        height: auto !important;
        min-height: 0 !important;
        margin-bottom: 0.25rem !important;
    }
    div[data-testid="stVerticalBlock"] button:hover {
        background: #f5f5f7 !important;
        border-color: #bbb !important;
    }
    div[data-testid="stVerticalBlock"] button[kind="primary"],
    div[data-testid="stVerticalBlock"] button[data-testid="stBaseButton-primary"] {
        background: #0071e3 !important;
        border-color: #0071e3 !important;
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    div[data-testid="stVerticalBlock"] button[kind="primary"]:hover,
    div[data-testid="stVerticalBlock"] button[data-testid="stBaseButton-primary"]:hover {
        background: #0077ed !important;
        border-color: #0077ed !important;
        color: #ffffff !important;
    }

    /* 场景信息卡 */
    .scene-info {
        background: #f5f5f7;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-top: 0.6rem;
    }
    .scene-info-title {
        font-size: 0.88rem;
        font-weight: 600;
        color: #1d1d1f;
        margin-bottom: 0.3rem;
    }
    .scene-info-meta {
        font-size: 0.75rem;
        color: #6e6e73;
        line-height: 1.6;
    }

    /* ASR 台词 */
    .asr-node {
        padding: 0.4rem 0;
        border-bottom: 1px solid #f0f0f0;
        font-size: 0.8rem;
        color: #1d1d1f;
        line-height: 1.5;
    }
    .asr-node:last-child { border-bottom: none; }
    .asr-speaker { font-weight: 600; color: #0071e3; font-size: 0.72rem; }
    .asr-time { font-size: 0.65rem; color: #86868b; font-family: 'Menlo', monospace; }

    /* 侧边栏 */
    section[data-testid="stSidebar"] { background: #ffffff !important; }
    section[data-testid="stSidebar"] * { color: #1d1d1f !important; }
    section[data-testid="stSidebar"] .stat-lbl { color: #6e6e73 !important; }
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
        background: #0071e3 !important; color: #ffffff !important;
        border: none !important; border-radius: 8px !important;
    }

    /* 统计 */
    .stat-row { display: flex; gap: 0.6rem; margin: 0.4rem 0; }
    .stat-item { flex: 1; text-align: center; background: #f5f5f7; border-radius: 8px; padding: 0.4rem; }
    .stat-val { font-size: 1.2rem; font-weight: 600; color: #1d1d1f; }
    .stat-lbl { font-size: 0.65rem; color: #6e6e73; text-transform: uppercase; letter-spacing: 0.04em; }

    /* 视频 */
    video { border-radius: 8px; }

    /* 滚动容器内部去边框 */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
        border-radius: 0 !important;
    }

    /* 滚动条 */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #d1d1d6; border-radius: 2px; }
    </style>""", unsafe_allow_html=True)


# ============================================================================
# 侧边栏
# ============================================================================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 视频剧本拆解实验室")

        projects = scan_projects()
        if not projects:
            st.info("results/ 下无结果文件")
            return

        project_names = sorted(projects.keys())
        selected_project = st.selectbox("项目 / 集数", project_names)
        st.markdown("---")

        groups = projects.get(selected_project, [])
        names = {0: "对照组: 纯ASR+人脸", 1: "ASR 主导", 2: "K-means 主导", 3: "LLM 自由推演", 4: "Qwen3.5-Omni-Flash", 5: "Qwen3.5-Omni-Plus"}

        def fmt_group(g):
            return names.get(g, str(g)) if g == 0 else f"实验组 {g}: {names.get(g, str(g))}"

        group = st.radio("实验组", groups, format_func=fmt_group)

        if st.button("加载结果", use_container_width=True, type="primary"):
            data = load_results(group, selected_project)
            if data:
                st.session_state.results = data
                st.session_state.outline_idx = 0
                st.session_state.detail_idx = 0
                st.session_state.current_project = selected_project
                st.rerun()

        if st.session_state.results:
            r = st.session_state.results
            st.markdown("---")
            st.markdown(f"**{r.get('experiment_name', '')}**")
            st.markdown(f"""<div class="stat-row">
                <div class="stat-item"><div class="stat-val">{r['total_outlines']}</div><div class="stat-lbl">大纲</div></div>
                <div class="stat-item"><div class="stat-val">{r['total_scenes']}</div><div class="stat-lbl">细纲</div></div>
            </div>""", unsafe_allow_html=True)

            summary = r.get("summary", {}).get("full_summary", "")
            if summary:
                st.markdown("---")
                st.caption("摘要")
                st.markdown(f"<div style='font-size:0.8rem;color:#424245;line-height:1.6'>{summary[:300]}{'...' if len(summary)>300 else ''}</div>", unsafe_allow_html=True)


# ============================================================================
# 实验对比弹窗
# ============================================================================
@st.dialog("实验组对比分析", width="large")
def show_comparison_dialog():
    projects = ['tpn01', 'tpn02', 'sgyy01', 'sbpk01', 'yxzt01']
    all_groups = [0, 1, 2, 3, 4, 5]
    group_labels = {0: 'G0 对照', 1: 'G1 ASR', 2: 'G2 Kmeans', 3: 'G3 自由', 4: 'G4 Flash', 5: 'G5 Plus'}

    data = {}
    for p in projects:
        data[p] = {}
        for g in all_groups:
            path = os.path.join(RESULTS_DIR, f"group{g}_{p}_result.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data[p][g] = json.load(f)

    labels = [group_labels[g] for g in all_groups]

    st.markdown("#### 颗粒度对比（大纲/细纲）")
    rows = []
    for p in projects:
        row = {"项目": p}
        for g in all_groups:
            if g in data[p]:
                r = data[p][g]
                row[group_labels[g]] = f"{r['total_outlines']}/{r['total_scenes']}"
            else:
                row[group_labels[g]] = "-"
        rows.append(row)
    st.table(rows)

    st.markdown("#### 细纲平均时长（秒）")
    rows2 = []
    for p in projects:
        row = {"项目": p}
        for g in all_groups:
            if g in data[p]:
                details = []
                for o in data[p][g]['outlines']:
                    for d in o.get('scene_details', []):
                        dur = d.get('end_time', 0) - d.get('start_time', 0)
                        if dur > 0:
                            details.append(dur)
                avg = sum(details) / len(details) if details else 0
                row[group_labels[g]] = f"{avg:.0f}"
            else:
                row[group_labels[g]] = "-"
        rows2.append(row)
    st.table(rows2)

    st.markdown("#### 细纲失败数（失败大纲/总大纲）")
    rows3 = []
    for p in projects:
        row = {"项目": p}
        for g in all_groups:
            if g in data[p]:
                r = data[p][g]
                failed = sum(1 for o in r['outlines'] if not o.get('scene_details'))
                total = len(r['outlines'])
                row[group_labels[g]] = f"{failed}/{total}"
            else:
                row[group_labels[g]] = "-"
        rows3.append(row)
    st.table(rows3)

    st.markdown("#### 大纲覆盖率（占视频总时长 %）")
    rows4 = []
    for p in projects:
        row = {"项目": p}
        # 获取该项目视频总时长
        max_time = 0
        for g in all_groups:
            if g in data[p]:
                for n in data[p][g].get('timeline_data', []):
                    t = n.get('end_time', n.get('timestamp', 0))
                    if t > max_time:
                        max_time = t
        row["时长"] = f"{max_time/60:.1f}m"
        for g in all_groups:
            if g in data[p]:
                covered = set()
                for o in data[p][g]['outlines']:
                    s, e = o.get('start_time', 0), o.get('end_time', 0)
                    if s and e:
                        for sec in range(int(s), int(e) + 1):
                            covered.add(sec)
                pct = len(covered) / max_time * 100 if max_time else 0
                row[group_labels[g]] = f"{pct:.1f}%"
            else:
                row[group_labels[g]] = "-"
        rows4.append(row)
    st.table(rows4)

    st.markdown("#### 细纲覆盖率（占视频总时长 %）")
    rows5 = []
    for p in projects:
        row = {"项目": p}
        max_time = 0
        for g in all_groups:
            if g in data[p]:
                for n in data[p][g].get('timeline_data', []):
                    t = n.get('end_time', n.get('timestamp', 0))
                    if t > max_time:
                        max_time = t
        for g in all_groups:
            if g in data[p]:
                covered = set()
                for o in data[p][g]['outlines']:
                    for d in o.get('scene_details', []):
                        s, e = d.get('start_time', 0), d.get('end_time', 0)
                        if s and e:
                            for sec in range(int(s), int(e) + 1):
                                covered.add(sec)
                pct = len(covered) / max_time * 100 if max_time else 0
                row[group_labels[g]] = f"{pct:.1f}%"
            else:
                row[group_labels[g]] = "-"
        rows5.append(row)
    st.table(rows5)

    st.markdown("#### 覆盖率分析")
    st.markdown("""
- **大纲覆盖率普遍 85-98%** — 各组都能覆盖绝大部分视频时长，差异较小
- **细纲覆盖率差异显著** — 这是区分实验组优劣的关键指标：
  - **G0 对照组和 G5 Qwen Plus 细纲覆盖最稳定**（70-90%），得益于零失败率
  - **G2 K-means 主导在 sgyy01/yxzt01 上细纲覆盖仅 25-27%**，因后半段大面积细纲生成失败
  - **G3 自由推演波动大** — tpn02 仅 66%，存在 280s 的连续空洞
  - **G4 Qwen Flash 的 yxzt01 细纲覆盖 35%**，虽然 gap 总量小但大量大纲本身无细纲
- **所有组共有的 gap** — 如 tpn01 的 892-952s、sgyy01 的 544-628s，属于视频中的广告/片花/无台词段，是输入数据本身的空白
    """)

    st.markdown("#### 失败原因分析")
    st.markdown("""
- **33 个失败中 30 个为 LLM 输出 JSON 解析失败**（模型返回了非标准 JSON），3 个为 ID 幻觉（Qwen Flash 输出了超出时间线范围的 ID）
- **非工程 Bug** — Pipeline 本身的重试、JSON 修复机制已生效，失败均为模型在 5 次重试后仍无法输出合规 JSON
- **G0 和 G5 零失败** — 对照组 prompt 结构简单，Qwen Plus 的 JSON 遵从度最高
- **G2 失败集中在后半段** — 视觉主导 prompt 在长视频后段累积误差，模型更易输出格式错误
    """)

    st.markdown("#### 核心结论")
    st.markdown("""
1. **K-means 关键帧显著提升颗粒度** — G1/G2/G3 相比 G0，大纲和细纲数量均翻倍
2. **G1（ASR 主导 + Gemini）综合最优** — 颗粒度最细、命名最准确
3. **G5（ASR 主导 + Qwen Plus）稳定性最佳** — 5 个项目零失败，颗粒度适中
4. **G2（K-means 主导）能捕捉画面转场但不稳定** — sgyy01/yxzt01 后半段大面积失败
5. **G3（自由推演）有创造性但不可控** — 命名偏文学化，偶尔脱离实际内容
6. **G4（Qwen Flash）明显不足** — 颗粒度最粗，yxzt01 几乎完全失效
7. **同 Prompt 下 Gemini 3.1 Pro > Qwen Plus > Qwen Flash** — G1 vs G5 vs G4 的直接对比
    """)
    st.caption("模型：Gemini 3.1 Pro Preview (G0-G3) / Qwen 3.5 Omni Flash (G4) / Qwen 3.5 Omni Plus (G5)")


# ============================================================================
# 主界面
# ============================================================================
def main():
    init_state()
    inject_css()
    render_sidebar()

    project = st.session_state.get("current_project", "tpn01")
    exp_name = st.session_state.results.get("experiment_name", "") if st.session_state.results else ""

    # 顶栏：标题 + 对比按钮
    top_left, top_right = st.columns([5, 1])
    with top_left:
        sub = f"<span class='top-bar-sub'>{project} · {exp_name}</span>" if exp_name else f"<span class='top-bar-sub'>{project}</span>"
        st.markdown(f"<div class='top-bar'><span class='top-bar-title'>视频剧本拆解实验室</span>{sub}</div>", unsafe_allow_html=True)
    with top_right:
        if st.button("实验对比", use_container_width=True):
            show_comparison_dialog()

    if not st.session_state.results:
        st.markdown("<div style='text-align:center;padding:4rem 0;color:#86868b;font-size:0.9rem'>在左侧选择实验组并加载结果</div>", unsafe_allow_html=True)
        return

    results = st.session_state.results
    outlines = results.get("outlines", [])

    # 三栏：大纲(1.5) | 细纲(1.5) | 视频+详情(2)
    col_outline, col_detail, col_video = st.columns([1.5, 1.5, 2])

    # ===== 大纲列 =====
    with col_outline:
        st.markdown('<div class="col-title">大纲</div>', unsafe_allow_html=True)
        with st.container(height=650):
            for idx, o in enumerate(outlines):
                selected = idx == st.session_state.outline_idx
                name = o.get("scene_name", f"场景 {idx+1}")
                t0, t1 = fmt(o.get("start_time")), fmt(o.get("end_time"))
                label = f"{idx+1}. {name}\n{t0} - {t1}"
                if st.button(label, key=f"o_{idx}", use_container_width=True,
                             type="primary" if selected else "secondary"):
                    st.session_state.outline_idx = idx
                    st.session_state.detail_idx = 0
                    st.rerun()

    # ===== 细纲列 =====
    with col_detail:
        st.markdown('<div class="col-title">细纲</div>', unsafe_allow_html=True)
        with st.container(height=650):
            if outlines and st.session_state.outline_idx < len(outlines):
                details = outlines[st.session_state.outline_idx].get("scene_details", [])
                if not details:
                    st.caption("该大纲暂无细纲")
                else:
                    for idx, d in enumerate(details):
                        selected = idx == st.session_state.detail_idx
                        name = d.get("scene_name", f"细纲 {idx+1}")
                        t0, t1 = fmt(d.get("start_time")), fmt(d.get("end_time"))
                        label = f"{idx+1}. {name}\n{t0} - {t1}"
                        if st.button(label, key=f"d_{idx}", use_container_width=True,
                                     type="primary" if selected else "secondary"):
                            st.session_state.detail_idx = idx
                            st.rerun()

    # ===== 视频 + 详情列 =====
    with col_video:
        st.markdown('<div class="col-title">视频预览</div>', unsafe_allow_html=True)

        start_sec = 0
        current_detail = None
        if outlines and st.session_state.outline_idx < len(outlines):
            details = outlines[st.session_state.outline_idx].get("scene_details", [])
            if details and st.session_state.detail_idx < len(details):
                current_detail = details[st.session_state.detail_idx]
                start_sec = int(current_detail.get("start_time", 0))

        if start_sec > 0:
            st.caption(f"视频定位: {fmt(start_sec)} (部署版不含视频文件)")
        else:
            st.caption("选择细纲可定位对应时间段")

        if current_detail:
            t0 = fmt(current_detail.get("start_time"))
            t1 = fmt(current_detail.get("end_time"))
            reason = current_detail.get("reason", "")
            st.markdown(f"""<div class="scene-info">
                <div class="scene-info-title">{current_detail.get('scene_name', '')}</div>
                <div class="scene-info-meta">
                    {t0} - {t1} &nbsp; ID {current_detail.get('first_clip_id', '')}-{current_detail.get('last_clip_id', '')}
                    {'<br>' + reason if reason else ''}
                </div>
            </div>""", unsafe_allow_html=True)

            timeline = results.get("timeline_data", [])
            fid = current_detail.get("first_clip_id", 0)
            lid = current_detail.get("last_clip_id", 0)
            nodes = [n for n in timeline if fid <= n["id"] <= lid and n["type"] == "asr"]

            if nodes:
                st.markdown("<div style='margin-top:0.8rem'></div>", unsafe_allow_html=True)
                st.markdown('<div class="col-title">台词</div>', unsafe_allow_html=True)
                with st.container(height=300):
                    for n in nodes:
                        speaker = n.get("speaker", "未知")
                        t = fmt(n.get("start_time", 0))
                        text = n.get("transcript", "")
                        st.markdown(f"""<div class="asr-node">
                            <span class="asr-time">{t}</span>
                            <span class="asr-speaker"> {speaker}</span><br>{text}
                        </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
