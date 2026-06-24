from pathlib import Path

from manus_request import generate_manus_request_file
from profit_calculator import create_profit_ranking
from report_generator import save_html_report


def main():
    project_root = Path(__file__).resolve().parent.parent
    candidate_path = project_root / "data" / "ebay_raw" / "ebay_candidates.csv"
    manus_request_path = project_root / "data" / "manus_requests" / "manus_request.csv"
    manus_result_path = project_root / "data" / "manus_results" / "manus_results.csv"
    fees_path = project_root / "config" / "fees.json"
    ranking_path = project_root / "data" / "processed" / "profit_ranking.csv"
    html_report_path = project_root / "reports" / "daily_report.html"

    requests = generate_manus_request_file(candidate_path, manus_request_path)
    ranking = create_profit_ranking(
        manus_request_path,
        manus_result_path,
        fees_path,
        ranking_path,
    )
    candidate_count, ranking_count = save_html_report(
        candidate_path,
        ranking_path,
        html_report_path,
    )

    print("Manus連携MVPパイプラインが完了しました。")
    print(f"eBay候補件数: {candidate_count}件")
    print(f"Manus依頼件数: {len(requests)}件")
    print(f"利益商品件数: {ranking_count}件")
    print(f"利益ランキング: {ranking_path}")
    print(f"HTMLレポート: {html_report_path}")


if __name__ == "__main__":
    main()
