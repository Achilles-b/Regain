#プロジェクトに対するcreate,edit,delete,project選択処理の定義

from flask import jsonify, Blueprint, request
from db_driver import dbDriver
import process
import datetime
import math

#プロジェクトのルーティング/
bp = Blueprint('project', __name__, url_prefix="/")
#プロセスへのルーティング情報
bp.register_blueprint(process.bp)

#新規プロジェクト作成
#受信JSON例
# {
#   "project_name":"projectのなまえ",
#   "estimated_time":"24:00"
# }
@bp.route('/create', methods=['POST'])
def project_create():
    params = request.get_json()
    project_name = params["project_name"]
    estimated_time = params.get("estimated_time","0:00")
    estimated_time += ":00"

    #dbDriverの生成
    regain_db_driver = dbDriver()
    
    #project生成SQL文
    project_insert_sql = f"""
                        INSERT INTO
                            projects (project_name, estimated_time)
                        VALUES
                            ('{project_name}', CAST('{estimated_time}' as TIME))
                        """
    rows = regain_db_driver.sql_run(project_insert_sql)
    rows = regain_db_driver.sql_run("COMMIT")

    #dbDriverのクローズと200OK返却
    regain_db_driver.db_close()
    return jsonify()

#既存プロジェクト編集
@bp.route('/edit', methods=['POST'])
def project_edit():
    return jsonify()

#既存プロジェクト削除
@bp.route('/delete', methods=['DELETE'])
def project_delete():
    return jsonify()

#既存プロジェクト選択、プロセス一覧表示
@bp.route('/<int:project_id>')
def process_get(project_id):
    
    #dbDriverの生成
    regain_db_driver = dbDriver()
    

    #本日の日付取得
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d")
    #本日の作業時間取得SQL
    today_commit_time_sql = f"""(
                            SELECT
                                processes.process_id,
                                IFNULL(SUM(TIME_TO_SEC(commit_time)), 0) as today_commit_time
                            FROM
                                processes
                                LEFT JOIN tasks
                                    ON processes.process_id = tasks.process_id
                                LEFT JOIN commits
                                    ON tasks.task_id = commits.task_id
                            WHERE
                                commit_date = '{now_str}'
                            GROUP BY
                                process_id
                        )"""

    #プロセス一覧取得SQL
    process_list_sql = f"""
                            SELECT
                                processes.process_id,
                                process_name,
                                DATE_FORMAT(processes.estimated_time,'%k:%i') as estimated_time,
                                TIME_TO_SEC(processes.estimated_time) as estimated_time_sec,
                                DATE_FORMAT(processes.deadline,'%c/%e') as deadline,
                                DATE_FORMAT(SEC_TO_TIME(IFNULL(SUM(TIME_TO_SEC(commit_time)), 0)),'%k:%i') as passed_time,
                                IFNULL(SUM(TIME_TO_SEC(commit_time)), 0) as passed_time_sec,
                                COUNT(DISTINCT commit_date) as passed_date,
                                IFNULL(today_commit_time, 0) as today_commit_time,
                                status_name
                            FROM
                                processes
                                LEFT JOIN tasks
                                    ON processes.process_id = tasks.process_id
                                LEFT JOIN commits
                                    ON tasks.task_id = commits.task_id
                                LEFT JOIN {today_commit_time_sql} as today_commit_time_table
                                    ON processes.process_id = today_commit_time_table.process_id
                                LEFT JOIN process_statuses
                                    ON processes.status_id = process_statuses.status_id
                            WHERE
                                processes.project_id = {project_id}
                            GROUP BY
                                process_id
                        """
    rows = regain_db_driver.sql_run(process_list_sql)

    #予測日数を計算
    for one_process in rows:
        #過去の作業記録がないプロセスのpredict_timeは-1
        if(one_process["passed_date"] == 0 or (one_process["today_commit_time"] > 0 and one_process["passed_date"] == 1)) :
            one_process["predict_time"] = -1
            continue
            
        #本日の作業分は除外して作業時間/日を計算する
        #予測時間への必要日数を計算したのち、作業日数を引いて残り予測日数を出す
        if(one_process["today_commit_time"] > 0):
            passed_time_par_day = (one_process["passed_time_sec"] - one_process["today_commit_time"]) / (one_process["passed_date"] - 1)
            required_day = one_process["estimated_time_sec"] / passed_time_par_day
            predict_time = required_day - (one_process["passed_date"] - 1)
        else:
            passed_time_par_day = one_process["passed_time_sec"]/ one_process["passed_date"]
            required_day = one_process["estimated_time_sec"] / passed_time_par_day
            predict_time = required_day - one_process["passed_date"]
        one_process["predict_time"] = math.ceil(predict_time)
    
    #dbDriverのクローズと値返却
    regain_db_driver.db_close()
    return jsonify(rows)