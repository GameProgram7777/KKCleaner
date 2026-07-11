# KKCleaner
# Copyright (c) 2024 GameProgram7777
# Licensed under the MIT License. See the LICENSE file for details.
import os
import csv
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, Frame, Label, Entry, Button, Checkbutton, BooleanVar, StringVar
import tkinterdnd2 as tkdnd
import chardet
import sys
import clr
# 添加 Mono.Cecil 的路徑
cecil_path = os.path.dirname(os.path.abspath(__file__))  # 假設 Mono.Cecil.dll 與腳本在同一目錄
sys.path.append(cecil_path)
clr.AddReference(os.path.join(cecil_path, 'Mono.Cecil'))  # 明確指定 DLL 檔案路徑

from Mono.Cecil import ModuleDefinition, ReaderParameters, DefaultAssemblyResolver




def load_plugin_info(dll_path):
    """從 DLL 檔案中讀取 plugin 的 GUID"""
    try:
        # 創建 DefaultAssemblyResolver
        resolver = DefaultAssemblyResolver()
        resolver.AddSearchDirectory(os.path.dirname(dll_path))

        # 讀取模組定義
        reader_params = ReaderParameters()
        reader_params.AssemblyResolver = resolver
        module = ModuleDefinition.ReadModule(dll_path, reader_params)

        # 查找 BepInEx.BepInPlugin 特性
        bepinex_plugin_type = None
        for type_ref in module.GetTypeReferences():
            if type_ref.FullName == "BepInEx.BepInPlugin":
                bepinex_plugin_type = type_ref
                break

        if not bepinex_plugin_type:
            print(f"No BepInEx.BepInPlugin type found in {dll_path}")
            return None

        # 遍歷所有類型，查找帶有 BepInEx.BepInPlugin 特性的類
        for type_def in module.Types:
            for custom_attr in type_def.CustomAttributes:
                if custom_attr.AttributeType.FullName == "BepInEx.BepInPlugin":
                    # 提取 GUID
                    if len(custom_attr.ConstructorArguments) >= 1:
                        guid = custom_attr.ConstructorArguments[0].Value  # 直接使用 Value，不需要 ToString()
                        return guid

        print(f"No GUID found in {dll_path}")
        return None
    except Exception as e:
        print(f"Error reading DLL {dll_path}: {str(e)}")
        return None
    finally:
        # 確保模組資源被釋放
        if 'module' in locals():
            module.Dispose()

class CSVType:
    MOD = "mod"
    PLUGIN = "plugin"

class Localizations:
    LANGUAGES = {
        'en': {
            'title': 'KK Cleaner',
            'upload_text': 'Drag and drop your CSV file here or click to upload',
            'detect': 'Detect',
            'action': 'Action',
            'min_usages': 'Minimum Card Usages',
            'run': 'Run',
            'browse': 'Browse',
            'action_pack': 'Pack',
            'action_undo_pack': 'Undo Pack',
            'action_remove': 'Remove',
            'language': 'Language:',
            'error_csv_upload': 'Only .csv files are allowed.',
            'error_upload': 'Upload Error',
            'error_no_csv': 'Please upload a CSV file first.',
            'error_mod_path': 'Please enter path',
            'error_invalid_path': 'The entered path is invalid.',
            'error_no_min_usage': 'Please enter minimum card usages.',
            'error_no_detection': 'Please detect first.',
            'error_unknown_action': 'Unknown action selected.',
            'error_no_data': 'No data found in CSV.',
            'nothing_to_undo': 'Nothing to undo.',
            'success_csv_upload': 'CSV uploaded successfully!',

            # messagebox 標題
            'result_title': 'Detection Results',
            'success_title': 'Success',
            'nothing_to_pack_title': 'Nothing to Pack',
            'nothing_to_remove_title': 'Nothing to Remove',
            'nothing_to_undo_title': 'Nothing to Undo',
            'error_pack_title': 'Pack Error',
            'error_remove_title': 'Remove Error',
            'error_undo_pack_title': 'Undo Pack Error',

            # 初始組合狀態的鍵值
            'mod_plugin_path': 'Mod/Plugin Path',
            'custom_mod_plugin': 'Custom Mods/Plugins Only',
            
            # Mod 專用鍵值
            'mod_path': 'Mod Path',
            'custom_mods': 'Custom Mods Only',
            'result_all_used': 'All mods have card usages above the minimum.',
            'result_low_usage_found': '{} mods found with card usages at or below the minimum.',
            'nothing_to_remove': 'No mods to remove.',
            'nothing_to_pack': 'No mods to pack.',
            'confirm_remove': 'Are you sure you want to remove {0} mod(s) with usage count at or below {1}?',
            'confirm_remove_title': 'Confirm Remove',
            'success_pack': 'Pack executed successfully! {} mods moved.',
            'success_remove': 'Remove executed successfully! {} mods removed.',
            'success_undo_pack': 'Undo Pack executed successfully! {} mods restored.',
            'error_pack': 'Failed to pack mods: {}',
            'error_remove': 'Failed to remove mods: {}',
            'error_undo_pack': 'Failed to undo pack: {}',
            
            # Plugin 專用鍵值
            'plugin_path': 'Plugin Path',
            'custom_plugins': 'Custom Plugins Only',
            'result_all_plugins_used': 'All plugins have card usages above the minimum.',
            'result_low_usage_plugins_found': '{} plugins found with card usages at or below the minimum.',
            'nothing_to_remove_plugin': 'No plugins to remove.',
            'nothing_to_pack_plugin': 'No plugins to pack.',
            'confirm_remove_plugin': 'Are you sure you want to remove {0} plugin(s) with usage count at or below {1}?',
            'success_pack_plugin': 'Pack executed successfully! {} plugins moved.',
            'success_remove_plugin': 'Remove executed successfully! {} plugins removed.',
            'success_undo_pack_plugin': 'Undo Pack executed successfully! {} plugins restored.',
            'error_pack_plugin': 'Failed to pack plugins: {}',
            'error_remove_plugin': 'Failed to remove plugins: {}',
            'error_undo_pack_plugin': 'Failed to undo pack: {}'
        },
        'zh-tw': {
            'title': 'KK 清理器', 
            'upload_text': '將 CSV 檔案拖曳至此處或點擊上傳',
            'detect': '偵測',
            'action': '操作',
            'min_usages': '最小卡片使用次數',
            'run': '執行',
            'browse': '瀏覽',
            'action_pack': '打包',
            'action_undo_pack': '復原打包',
            'action_remove': '移除',
            'language': '語言：',
            'error_csv_upload': '只能上傳 .csv 檔案',
            'error_upload': '上傳錯誤',
            'error_no_csv': '請先上傳 CSV 檔案',
            'error_mod_path': '請輸入路徑',
            'error_invalid_path': '輸入的路徑無效',
            'error_no_min_usage': '請輸入最小卡片使用次數',
            'error_no_detection': '請先進行偵測',
            'error_unknown_action': '選擇了未知的操作',
            'error_no_data': 'CSV 檔案中沒有發現任何資料',
            'nothing_to_undo': '沒有可復原的項目',
            'success_csv_upload': 'CSV 上傳成功！',

            # messagebox 標題
            'result_title': '偵測結果',
            'success_title': '成功',
            'nothing_to_pack_title': '沒有可打包的項目',
            'nothing_to_remove_title': '沒有可移除的項目',
            'nothing_to_undo_title': '沒有可復原的項目',
            'error_pack_title': '打包錯誤',
            'error_remove_title': '移除錯誤',
            'error_undo_pack_title': '復原打包錯誤',

            # 初始組合狀態的鍵值
            'mod_plugin_path': '模組/插件路徑',
            'custom_mod_plugin': '僅限自訂模組/插件',
            
            # Mod 專用鍵值
            'mod_path': '模組路徑',
            'custom_mods': '僅限自訂模組',
            'result_all_used': '所有模組使用次數皆高於最小值',
            'result_low_usage_found': '找到 {} 個使用次數低於或等於最小值的模組',
            'nothing_to_remove': '沒有可移除的模組',
            'nothing_to_pack': '沒有可打包的模組',
            'confirm_remove': '您確定要移除 {0} 個使用次數在{1}次以下的模組嗎？',
            'confirm_remove_title': '確認移除',
            'success_pack': '打包執行成功！已移動 {} 個模組',
            'success_remove': '移除執行成功！已移除 {} 個模組',
            'success_undo_pack': '復原打包執行成功！已還原 {} 個模組',
            'error_pack': '打包模組失敗：{}',
            'error_remove': '移除模組失敗：{}',
            'error_undo_pack': '復原打包失敗：{}',
            
            # Plugin 專用鍵值
            'plugin_path': '插件路徑',
            'custom_plugins': '僅限自訂插件',
            'result_all_plugins_used': '所有插件使用次數皆高於最小值',
            'result_low_usage_plugins_found': '找到 {} 個使用次數低於或等於最小值的插件',
            'nothing_to_remove_plugin': '沒有可移除的插件',
            'nothing_to_pack_plugin': '沒有可打包的插件',
            'confirm_remove_plugin': '您確定要移除 {0} 個使用次數在{1}次以下的插件嗎？',
            'success_pack_plugin': '打包執行成功！已移動 {} 個插件',
            'success_remove_plugin': '移除執行成功！已移除 {} 個插件',
            'success_undo_pack_plugin': '復原打包執行成功！已還原 {} 個插件',
            'error_pack_plugin': '打包插件失敗：{}',
            'error_remove_plugin': '移除插件失敗：{}',
            'error_undo_pack_plugin': '復原打包失敗：{}'
        },
        'zh-cn': {
            'title': 'KK 清理器',
            'upload_text': '将 CSV 文件拖拽至此处或点击上传',
            'detect': '检测',
            'action': '操作',
            'min_usages': '最小卡片使用次数',
            'run': '执行',
            'browse': '浏览',
            'action_pack': '打包',
            'action_undo_pack': '撤销打包',
            'action_remove': '移除',
            'language': '语言：',
            'error_csv_upload': '只能上传 .csv 文件',
            'error_upload': '上传错误',
            'error_no_csv': '请先上传 CSV 文件',
            'error_mod_path': '请输入路径',
            'error_invalid_path': '输入的路径无效',
            'error_no_min_usage': '请输入最小卡片使用次数',
            'error_no_detection': '请先进行检测',
            'error_unknown_action': '选择了未知的操作',
            'error_no_data': 'CSV 文件中没有发现任何数据',
            'nothing_to_undo': '没有可撤销的项目',
            'success_csv_upload': 'CSV 上传成功！',

            # messagebox 標題
            'result_title': '检测结果',
            'success_title': '成功',
            'nothing_to_pack_title': '没有可打包的项目',
            'nothing_to_remove_title': '没有可移除的项目',
            'nothing_to_undo_title': '没有可撤销的项目',
            'error_pack_title': '打包错误',
            'error_remove_title': '移除错误',
            'error_undo_pack_title': '撤销打包错误',

            # 初始组合状态的键值
            'mod_plugin_path': '模组/插件路径',
            'custom_mod_plugin': '仅限自定义模组/插件',
            
            # Mod 专用键值
            'mod_path': '模组路径',
            'custom_mods': '仅限自定义模组',
            'result_all_used': '所有模组使用次数均高于最小值',
            'result_low_usage_found': '找到 {} 个使用次数低于或等于最小值的模组',
            'nothing_to_remove': '没有可移除的模组',
            'nothing_to_pack': '没有可打包的模组',
            'confirm_remove': '您确定要移除 {0} 个使用次数在{1}次以下的模组吗？',
            'confirm_remove_title': '确认移除',
            'success_pack': '打包执行成功！已移动 {} 个模组',
            'success_remove': '移除执行成功！已移除 {} 个模组',
            'success_undo_pack': '撤销打包执行成功！已还原 {} 个模组',
            'error_pack': '打包模组失败：{}',
            'error_remove': '移除模组失败：{}',
            'error_undo_pack': '撤销打包失败：{}',
            
            # Plugin 专用键值
            'plugin_path': '插件路径',
            'custom_plugins': '仅限自定义插件',
            'result_all_plugins_used': '所有插件使用次数均高于最小值',
            'result_low_usage_plugins_found': '找到 {} 个使用次数低于或等于最小值的插件',
            'nothing_to_remove_plugin': '没有可移除的插件',
            'nothing_to_pack_plugin': '没有可打包的插件',
            'confirm_remove_plugin': '您确定要移除 {0} 个使用次数在{1}次以下的插件吗？',
            'success_pack_plugin': '打包执行成功！已移动 {} 个插件',
            'success_remove_plugin': '移除执行成功！已移除 {} 个插件',
            'success_undo_pack_plugin': '撤销打包执行成功！已还原 {} 个插件',
            'error_pack_plugin': '打包插件失败：{}',
            'error_remove_plugin': '移除插件失败：{}',
            'error_undo_pack_plugin': '撤销打包失败：{}'
        },
        'ja': {
            'title': 'KK クリーナー',
            'upload_text': 'CSVファイルをここにドラッグ＆ドロップするかアップロード',
            'detect': '検出',
            'action': 'アクション',
            'min_usages': '最小カード使用回数',
            'run': '実行',
            'browse': '参照',
            'action_pack': 'パック',
            'action_undo_pack': 'パックを取り消す',
            'action_remove': '削除',
            'language': '言語：',
            'error_csv_upload': '.csvファイルのみ許可されています',
            'error_upload': 'アップロードエラー',
            'error_no_csv': 'まずCSVファイルをアップロードしてください',
            'error_mod_path': 'パスを入力してください',
            'error_invalid_path': '入力されたパスは無効です',
            'error_no_min_usage': '最小カード使用回数を入力してください',
            'error_no_detection': '先に検出を実行してください',
            'error_unknown_action': '未知のアクションが選択されました',
            'error_no_data': 'CSVにデータが見つかりません',
            'nothing_to_undo': '取り消すものがありません',
            'success_csv_upload': 'CSVのアップロードに成功しました！',

            # messagebox 標題
            'result_title': '検出結果',
            'success_title': '成功',
            'nothing_to_pack_title': 'パックするものがありません',
            'nothing_to_remove_title': '削除するものがありません',
            'nothing_to_undo_title': '取り消すものがありません',
            'error_pack_title': 'パックエラー',
            'error_remove_title': '削除エラー',
            'error_undo_pack_title': 'パック取り消しエラー',

            # 初期組み合わせ状態のキー値
            'mod_plugin_path': 'MOD/プラグインパス',
            'custom_mod_plugin': 'カスタムMOD/プラグインのみ',
            
            # MOD専用キー値
            'mod_path': 'MODパス',
            'custom_mods': 'カスタムMODのみ',
            'result_all_used': 'すべてのMODの使用回数が最小値を上回っています',
            'result_low_usage_found': '使用回数が最小値以下のMODが {} 個見つかりました',
            'nothing_to_remove': '削除するMODがありません',
            'nothing_to_pack': 'パックするMODがありません',
            'confirm_remove': '使用回数が{1}回以下のMOD {0} 個を削除してもよろしいですか？',
            'confirm_remove_title': '削除の確認',
            'success_pack': 'パックが正常に実行されました！ {} 個のMODが移動されました',
            'success_remove': '削除が正常に実行されました！ {} 個のMODが削除されました',
            'success_undo_pack': 'パックの取り消しが正常に実行されました！ {} 個のMODが復元されました',
            'error_pack': 'MODのパックに失敗しました：{}',
            'error_remove': 'MODの削除に失敗しました：{}',
            'error_undo_pack': 'パックの取り消しに失敗しました：{}',
            
            # プラグイン専用キー値
            'plugin_path': 'プラグインパス',
            'custom_plugins': 'カスタムプラグインのみ',
            'result_all_plugins_used': 'すべてのプラグインの使用回数が最小値を上回っています',
            'result_low_usage_plugins_found': '使用回数が最小値以下のプラグインが {} 個見つかりました',
            'nothing_to_remove_plugin': '削除するプラグインがありません',
            'nothing_to_pack_plugin': 'パックするプラグインがありません',
            'confirm_remove_plugin': '使用回数が{1}回以下のプラグイン {0} 個を削除してもよろしいですか？',
            'success_pack_plugin': 'パックが正常に実行されました！ {} 個のプラグインが移動されました',
            'success_remove_plugin': '削除が正常に実行されました！ {} 個のプラグインが削除されました',
            'success_undo_pack_plugin': 'パックの取り消しが正常に実行されました！ {} 個のプラグインが復元されました',
            'error_pack_plugin': 'プラグインのパックに失敗しました：{}',
            'error_remove_plugin': 'プラグインの削除に失敗しました：{}',
            'error_undo_pack_plugin': 'パックの取り消しに失敗しました：{}'
        },
        'ko': {
            'title': 'KK 클리너',
            'upload_text': 'CSV 파일을 여기에 끌어다 놓거나 클릭하여 업로드',
            'detect': '감지',
            'action': '작업',
            'min_usages': '최소 카드 사용 횟수',
            'run': '실행',
            'browse': '찾아보기',
            'action_pack': '패킹',
            'action_undo_pack': '패킹 취소',
            'action_remove': '제거',
            'language': '언어:',
            'error_csv_upload': '.csv 파일만 허용됩니다',
            'error_upload': '업로드 오류',
            'error_no_csv': '먼저 CSV 파일을 업로드하세요',
            'error_mod_path': '경로를 입력하세요',
            'error_invalid_path': '입력한 경로가 잘못되었습니다',
            'error_no_min_usage': '최소 카드 사용 횟수를 입력하세요',
            'error_no_detection': '먼저 감지를 실행하세요',
            'error_unknown_action': '알 수 없는 작업이 선택되었습니다',
            'error_no_data': 'CSV 파일에 데이터가 없습니다',
            'nothing_to_undo': '취소할 항목이 없습니다',
            'success_csv_upload': 'CSV 업로드 성공!',

            # messagebox 標題
            'result_title': '감지 결과',
            'success_title': '성공',
            'nothing_to_pack_title': '패킹할 항목 없음',
            'nothing_to_remove_title': '제거할 항목 없음',
            'nothing_to_undo_title': '취소할 항목 없음',
            'error_pack_title': '패킹 오류',
            'error_remove_title': '제거 오류',
            'error_undo_pack_title': '패킹 취소 오류',

            # 초기 결합 상태 키값
            'mod_plugin_path': '모드/플러그인 경로',
            'custom_mod_plugin': '사용자 지정 모드/플러그인만',
            
            # 모드 전용 키값
            'mod_path': '모드 경로',
            'custom_mods': '사용자 지정 모드만',
            'result_all_used': '모든 모드의 사용 횟수가 최소값보다 높습니다',
            'result_low_usage_found': '사용 횟수가 최소값 이하인 모드 {} 개 발견',
            'nothing_to_remove': '제거할 모드가 없습니다',
            'nothing_to_pack': '패킹할 모드가 없습니다',
            'confirm_remove': '사용 횟수가 {1}회 이하인 모드 {0} 개를 제거하시겠습니까?',
            'confirm_remove_title': '제거 확인',
            'success_pack': '패킹 실행 성공! {} 개 모드 이동됨',
            'success_remove': '제거 실행 성공! {} 개 모드 제거됨',
            'success_undo_pack': '패킹 취소 실행 성공! {} 개 모드 복원됨',
            'error_pack': '모드 패킹 실패: {}',
            'error_remove': '모드 제거 실패: {}',
            'error_undo_pack': '패킹 취소 실패: {}',
            
            # 플러그인 전용 키값
            'plugin_path': '플러그인 경로',
            'custom_plugins': '사용자 지정 플러그인만',
            'result_all_plugins_used': '모든 플러그인의 사용 횟수가 최소값보다 높습니다',
            'result_low_usage_plugins_found': '사용 횟수가 최소값 이하인 플러그인 {} 개 발견',
            'nothing_to_remove_plugin': '제거할 플러그인이 없습니다',
            'nothing_to_pack_plugin': '패킹할 플러그인이 없습니다',
            'confirm_remove_plugin': '사용 횟수가 {1}회 이하인 플러그인 {0} 개를 제거하시겠습니까?',
            'success_pack_plugin': '패킹 실행 성공! {} 개 플러그인 이동됨',
            'success_remove_plugin': '제거 실행 성공! {} 개 플러그인 제거됨',
            'success_undo_pack_plugin': '패킹 취소 실행 성공! {} 개 플러그인 복원됨',
            'error_pack_plugin': '플러그인 패킹 실패: {}',
            'error_remove_plugin': '플러그인 제거 실패: {}',
            'error_undo_pack_plugin': '패킹 취소 실패: {}'
        },
        'ru': {
            'title': 'KK Cleaner',
            'upload_text': 'Перетащите CSV-файл сюда или нажмите для загрузки',
            'detect': 'Обнаружить',
            'action': 'Действие',
            'min_usages': 'Минимальное количество использований карт',
            'run': 'Выполнить',
            'browse': 'Обзор',
            'action_pack': 'Упаковка',
            'action_undo_pack': 'Отмена упаковки',
            'action_remove': 'Удаление',
            'language': 'Язык:',
            'error_csv_upload': 'Разрешены только файлы .csv',
            'error_upload': 'Ошибка загрузки',
            'error_no_csv': 'Сначала загрузите CSV-файл',
            'error_mod_path': 'Введите путь',
            'error_invalid_path': 'Введён неверный путь',
            'error_no_min_usage': 'Введите минимальное количество использований карт',
            'error_no_detection': 'Сначала выполните обнаружение',
            'error_unknown_action': 'Выбрано неизвестное действие',
            'error_no_data': 'В CSV не найдены данные',
            'nothing_to_undo': 'Нечего отменять',
            'success_csv_upload': 'CSV успешно загружен!',

            # messagebox 標題
            'result_title': 'Результаты обнаружения',
            'success_title': 'Успех',
            'nothing_to_pack_title': 'Нечего упаковывать',
            'nothing_to_remove_title': 'Нечего удалять',
            'nothing_to_undo_title': 'Нечего отменять',
            'error_pack_title': 'Ошибка упаковки',
            'error_remove_title': 'Ошибка удаления',
            'error_undo_pack_title': 'Ошибка отмены упаковки',

            # Ключи для начального комбинированного состояния
            'mod_plugin_path': 'Путь к модам/плагинам',
            'custom_mod_plugin': 'Только пользовательские моды/плагины',
            
            # Ключи для модов
            'mod_path': 'Путь к модам',
            'custom_mods': 'Только пользовательские моды',
            'result_all_used': 'Все моды используются выше минимума',
            'result_low_usage_found': 'Найдено {} модов с использованием не выше минимума',
            'nothing_to_remove': 'Нечего удалять из модов',
            'nothing_to_pack': 'Нечего упаковывать из модов',
            'confirm_remove': 'Вы уверены, что хотите удалить {0} модов с количеством использований не более {1}?',
            'confirm_remove_title': 'Подтвердить удаление',
            'success_pack': 'Упаковка выполнена успешно! Перемещено {} модов',
            'success_remove': 'Удаление выполнено успешно! Удалено {} модов',
            'success_undo_pack': 'Отмена упаковки выполнена успешно! Восстановлено {} модов',
            'error_pack': 'Не удалось упаковать моды: {}',
            'error_remove': 'Не удалось удалить моды: {}',
            'error_undo_pack': 'Не удалось отменить упаковку: {}',
            
            # Ключи для плагинов
            'plugin_path': 'Путь к плагинам',
            'custom_plugins': 'Только пользовательские плагины',
            'result_all_plugins_used': 'Все плагины используются выше минимума',
            'result_low_usage_plugins_found': 'Найдено {} плагинов с использованием не выше минимума',
            'nothing_to_remove_plugin': 'Нечего удалять из плагинов',
            'nothing_to_pack_plugin': 'Нечего упаковывать из плагинов',
            'confirm_remove_plugin': 'Вы уверены, что хотите удалить {0} плагинов с количеством использований не более {1}?',
            'success_pack_plugin': 'Упаковка выполнена успешно! Перемещено {} плагинов',
            'success_remove_plugin': 'Удаление выполнено успешно! Удалено {} плагинов',
            'success_undo_pack_plugin': 'Отмена упаковки выполнена успешно! Восстановлено {} плагинов',
            'error_pack_plugin': 'Не удалось упаковать плагины: {}',
            'error_remove_plugin': 'Не удалось удалить плагины: {}',
            'error_undo_pack_plugin': 'Не удалось отменить упаковку: {}'
        }
    }

class KKCleanerTool:
    def __init__(self, master):
        self.master = master
        self.current_language = StringVar(value='en')
        self.current_language.trace_add('write', self.change_language)
        
        # 初始化變數
        self.csv_file = None
        self.csv_type = None
        self.detection_performed = False
        self.low_usage_items = []
        self.base_path = None
        self.moved_files = {}
        self.current_action_index = 0
        
        # 配置主窗口
        self.setup_window()
        self.create_widgets()
        
        # 配置拖放功能
        self.setup_drag_drop()



    def change_language(self, *args, **kwargs):
            """語言切換處理"""
            if hasattr(self, 'action_combo'):
                self.current_action_index = self.action_combo.current()
            self.update_ui_elements()

    def on_action_change(self, *args):
        """操作選項變更處理"""
        self.current_action_index = self.action_combo.current()


    def update_ui_elements(self):
            """更新UI元素"""
            self.master.title(self.get_localized_text('title'))
            self.language_label.config(text=self.get_localized_text('language'))
            self.drop_area.config(text=self.get_localized_text('upload_text'))
            self.detect_button.config(text=self.get_localized_text('detect'))
            self.path_label.config(text=self.get_localized_text('mod_plugin_path'))
            self.browse_button.config(text=self.get_localized_text('browse'))
            self.action_label.config(text=self.get_localized_text('action'))
            self.custom_checkbox.config(text=self.get_localized_text('custom_mod_plugin'))
            self.min_usages_label.config(text=self.get_localized_text('min_usages'))
            self.run_button.config(text=self.get_localized_text('run'))

            actions = [
                self.get_localized_text('action_pack'),
                self.get_localized_text('action_undo_pack'),
                self.get_localized_text('action_remove')
            ]
            self.action_combo.config(values=actions)
            self.action_combo.current(self.current_action_index)
            self.action_combo_var.set(actions[self.current_action_index])

    def update_usage_range(self, usages):
        """更新使用次數範圍顯示"""
        if usages:
            min_usage = min(usages)
            max_usage = max(usages)
            self.usage_range_label.config(text=f"({min_usage}, {max_usage})")
        else:
            self.usage_range_label.config(text="")

    def update_ui_for_csv_type(self):
        """根據CSV類型更新UI"""
        self.path_label.config(text=self.get_localized_text('mod_plugin_path'))
        self.custom_checkbox.config(text=self.get_localized_text('custom_mod_plugin'))
        
    def show_detection_results(self):
        """顯示檢測結果"""
        if not self.low_usage_items:
            key = "result_all_plugins_used" if self.csv_type == CSVType.PLUGIN else "result_all_used"
            messagebox.showinfo(
                self.get_localized_text("result_title"), 
                self.get_localized_text(key)
            )
        else:
            key = "result_low_usage_plugins_found" if self.csv_type == CSVType.PLUGIN else "result_low_usage_found"
            messagebox.showinfo(
                self.get_localized_text("result_title"), 
                self.get_localized_text(key, len(self.low_usage_items))
            )


    def upload_csv(self, event=None):
        file_path = filedialog.askopenfilename(
            title="Upload CSV", 
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_path and file_path.endswith('.csv'):
            self.load_csv(file_path)


    def manual_mod_path_input(self, event=None):
        """處理手動輸入模組路徑"""
        path = self.path_input.get().strip()
        if path and os.path.exists(path) and os.path.isdir(path):
            self.base_path = path
            print(f"Path manually set to: {path}")
        else:
            print(f"Invalid path entered: {path}")


    def browse_mod_path(self):
        """開啟資料夾選擇對話框"""
        path = filedialog.askdirectory(title="Select Mod/Plugin Directory")
        if path:
            self.path_input.delete(0, tk.END)
            self.path_input.insert(0, path)
            self.base_path = path
            print(f"Path set to: {path}")




    def create_widgets(self):
            """建立 UI 元件"""
            # Main frame
            main_frame = Frame(self.master, bg='#f0f0f0')
            main_frame.pack(padx=20, pady=20, fill='both', expand=True)

            # Language Selector
            language_frame = Frame(main_frame, bg='#f0f0f0')
            language_frame.pack(fill='x', pady=(0, 10))

            self.language_label = Label(
                language_frame,
                text=self.get_localized_text('language'),
                bg='#f0f0f0'
            )
            self.language_label.pack(side='left', padx=(0, 10))

            # 顯示語言名稱對應的母語
            language_display_names = {
                'en': 'English',
                'zh-tw': '繁體中文',
                'zh-cn': '简体中文',
                'ja': '日本語',
                'ko': '한국어',
                'ru': 'Русский'
            }

            # 建立語言選擇下拉選單
            self.language_combo = ttk.Combobox(
                language_frame,
                state='readonly',
                values=[language_display_names[lang] for lang in Localizations.LANGUAGES.keys()],
                width=10
            )
            current_language_index = list(Localizations.LANGUAGES.keys()).index(self.current_language.get())
            self.language_combo.current(current_language_index)
            self.language_combo.pack(side='left')

            # 綁定語言切換事件
            def on_language_change(event):
                selected_index = self.language_combo.current()
                selected_language = list(Localizations.LANGUAGES.keys())[selected_index]
                self.current_language.set(selected_language)

            self.language_combo.bind("<<ComboboxSelected>>", on_language_change)

            # Minimum Card Usages Selection
            min_usages_frame = Frame(main_frame, bg='#f0f0f0')
            min_usages_frame.pack(pady=5)

            self.min_usages_label = Label(
                min_usages_frame,
                text=self.get_localized_text('min_usages'),
                bg='#f0f0f0'
            )
            self.min_usages_label.pack(side='left')

            self.min_usages_var = StringVar(value='0')
            self.min_usages_entry = Entry(
                min_usages_frame,
                textvariable=self.min_usages_var,
                width=5
            )
            self.min_usages_entry.pack(side='left', padx=(0, 10))

            self.usage_range_label = Label(
                min_usages_frame,
                text='',
                bg='#f0f0f0'
            )
            self.usage_range_label.pack(side='left')

            # CSV Upload Area
            self.drop_area = tk.Label(
                main_frame,
                text=self.get_localized_text('upload_text'),
                bg='white',
                fg='gray',
                font=('Arial', 12),
                width=50,
                height=10,
                relief='groove',
                borderwidth=2
            )
            self.drop_area.pack(pady=10, padx=10, fill='both', expand=True)
            self.drop_area.bind("<Button-1>", self.upload_csv)

            # Detect Button
            self.detect_button = Button(
                main_frame,
                text=self.get_localized_text('detect'),
                command=self.detect_low_usage_items
            )
            self.detect_button.pack(pady=5)

            # Path Input
            path_frame = Frame(main_frame, bg='#f0f0f0')
            path_frame.pack(pady=5, padx=10, fill='x')

            self.path_label = Label(
                path_frame,
                text=self.get_localized_text('mod_plugin_path'),
                bg='#f0f0f0'
            )
            self.path_label.pack(side='top', anchor='w')

            self.path_input = Entry(path_frame, width=40)
            self.path_input.pack(side='left', expand=True, fill='x', padx=(0, 10))
            self.path_input.bind('<KeyRelease>', self.manual_mod_path_input)

            self.browse_button = Button(
                path_frame,
                text=self.get_localized_text('browse'),
                command=self.browse_mod_path
            )
            self.browse_button.pack(side='right')

            # Action Selection
            action_frame = Frame(main_frame, bg='#f0f0f0')
            action_frame.pack(pady=5)

            self.action_label = Label(
                action_frame,
                text=self.get_localized_text('action'),
                bg='#f0f0f0'
            )
            self.action_label.pack(side='top')

            # Action Combo Box
            self.action_combo_var = StringVar()
            self.action_combo = ttk.Combobox(
                action_frame,
                textvariable=self.action_combo_var,
                state="readonly"
            )
            self.action_combo.pack(pady=5)
            
            actions = [
                self.get_localized_text('action_pack'),
                self.get_localized_text('action_undo_pack'),
                self.get_localized_text('action_remove')
            ]
            self.action_combo.config(values=actions)
            self.action_combo.current(0)
            self.current_action_index = 0
            
            # Custom Checkbox
            custom_mods_frame = Frame(main_frame, bg='#f0f0f0')
            custom_mods_frame.pack(pady=5)

            self.custom_mods_var = BooleanVar()
            self.custom_checkbox = Checkbutton(
                custom_mods_frame,
                text=self.get_localized_text('custom_mod_plugin'),
                variable=self.custom_mods_var,
                bg='#f0f0f0'
            )
            self.custom_checkbox.pack()

            # Run Button
            self.run_button = Button(
                main_frame,
                text=self.get_localized_text('run'),
                command=self.execute_action
            )
            self.run_button.pack(pady=5)

    def setup_window(self):
        """設置主窗口"""
        self.master.title("KK Cleaner")
        self.master.geometry("600x550")
        self.master.configure(bg='#f0f0f0')
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', background='#4CAF50', foreground='white')
        self.style.configure('TCombobox', background='white')

    def setup_drag_drop(self):
        """設置拖放功能"""
        self.master.drop_target_register(tkdnd.DND_FILES)
        self.master.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        """處理文件拖放"""
        dropped_file = event.data
        dropped_file = dropped_file.strip('{}').strip('"')
        
        if dropped_file.lower().endswith('.csv'):
            self.load_csv(dropped_file)
        else:
            messagebox.showerror(
                self.get_localized_text('error_upload'), 
                self.get_localized_text('error_csv_upload')
            )

    def get_localized_text(self, key, *args):
        """Get localized text for the current language"""
        lang = self.current_language.get()
        text = Localizations.LANGUAGES.get(lang, Localizations.LANGUAGES['en']).get(key, key)
        return text.format(*args) if args else text

    # 輔助方法
    def get_target_folder(self):
        """獲取目標資料夾名稱"""
        return "low_usage_plugins" if self.csv_type == CSVType.PLUGIN else "low_usage_mods"

    def get_target_folder_path(self):
        """獲取目標資料夾完整路徑"""
        return os.path.normpath(os.path.join(self.base_path, self.get_target_folder()))

    def walk_files(self, base_path, exclude_dir=None):
        """遍歷文件的輔助方法，排除指定目錄"""
        for root, dirs, files in os.walk(base_path):
            if exclude_dir and os.path.abspath(root) == os.path.abspath(exclude_dir):
                dirs.clear()  # 不遍歷被排除的目錄
                continue
            yield from ((root, file) for file in files)

    def safe_remove_file(self, file_path):
        """安全地刪除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error removing file {file_path}: {str(e)}")
            return False

    def safe_move_file(self, source, dest):
        """安全地移動文件"""
        try:
            if os.path.exists(source):
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(source, dest)
                return True
            return False
        except Exception as e:
            print(f"Error moving file from {source} to {dest}: {str(e)}")
            return False

    def clean_empty_folder(self, folder_path):
        """清理空資料夾"""
        try:
            if os.path.exists(folder_path) and not os.listdir(folder_path):
                os.rmdir(folder_path)
                print(f"Removed empty folder: {folder_path}")
                return True
            return False
        except Exception as e:
            print(f"Error removing empty folder {folder_path}: {str(e)}")
            return False

    def validate_detection(self):
        """驗證檢測條件"""
        if self.csv_file is None:
            messagebox.showerror(
                self.get_localized_text("error_upload"), 
                self.get_localized_text("error_no_csv")
            )
            return False

        if not self.min_usages_var.get().strip():
            messagebox.showerror(
                self.get_localized_text("error_upload"), 
                self.get_localized_text("error_no_min_usage")
            )
            return False
            
        try:
            int(self.min_usages_var.get())
        except ValueError:
            messagebox.showerror(
                self.get_localized_text("error_upload"), 
                self.get_localized_text("error_no_min_usage")
            )
            return False
            
        return True

    def validate_action(self):
        """驗證執行操作的條件"""
        if not self.detection_performed:
            messagebox.showerror(
                self.get_localized_text("error_upload"),
                self.get_localized_text("error_no_detection")
            )
            return False
            
        path_input = self.path_input.get().strip()
        if not path_input:
            messagebox.showerror(
                self.get_localized_text("error_upload"),
                self.get_localized_text("error_mod_path")
            )
            return False
            
        if not os.path.exists(path_input) or not os.path.isdir(path_input):
            messagebox.showerror(
                self.get_localized_text("error_upload"),
                self.get_localized_text("error_invalid_path")
            )
            return False
            
        self.base_path = path_input
        return True
    

    def detect_csv_encoding(self, file_path):
            """檢測 CSV 文件的編碼"""
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'

    def detect_csv_type(self, file_path):
        """檢測 CSV 文件類型"""
        try:
            encoding = self.detect_csv_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                first_row = next(reader)  # 讀取第一行（標題行）
                header_row = next(reader)  # 讀取第二行（欄位名稱行）
                
                # 通過檢查標題行和欄位名稱來判斷類型
                first_row_text = ' '.join(first_row).lower()
                
                # 檢查是否為插件CSV
                if "plugins used by" in first_row_text:
                    return CSVType.PLUGIN
                
                # 檢查是否為Mod CSV
                if "chara zipmods" in first_row_text:
                    # 驗證Mod CSV的欄位名稱
                    expected_mod_fields = {"guid", "cards with usages", "is installed", "zipmod filename"}
                    header_fields = {field.lower().strip() for field in header_row}
                    if expected_mod_fields.issubset(header_fields):
                        return CSVType.MOD
                    
            return None
        except Exception as e:
            print(f"Error detecting CSV type: {str(e)}")
            return None

    def load_csv(self, file_path):
        """載入並解析 CSV 文件"""
        try:
            self.csv_type = self.detect_csv_type(file_path)
            if not self.csv_type:
                raise ValueError("Invalid CSV format")

            encoding = self.detect_csv_encoding(file_path)
            self.csv_file = []
            
            with open(file_path, 'r', encoding=encoding) as f:
                lines = f.readlines()
                if self.csv_type == CSVType.PLUGIN:
                    print("Loading plugin CSV")
                    for line in lines[2:]:  # 跳過標題行和欄位名稱行
                        if line.strip():
                            parts = line.strip().split(',', 1)
                            if len(parts) >= 2:
                                plugin_name = parts[0].strip()
                                usage_str = parts[1].strip()
                                
                                # 從插件名稱中提取 GUID
                                guid = plugin_name.replace(".dll", "").strip()
                                
                                # 從使用次數字串中提取第一段連續數字
                                # （不可串接所有數字："3 (2 disabled)" 會變成 32）
                                match = re.search(r'\d+', usage_str)
                                usage = int(match.group()) if match else 0
                                
                                if guid:  # 只有在有效的 GUID 時才添加
                                    self.csv_file.append({
                                        'GUID': guid,
                                        'Cards with usages': usage,
                                        'Is installed': 'yes',  # 假設列在 CSV 中的插件都是已安裝的
                                        'Filename': f"{guid}.dll"
                                    })
                                    print(f"Loaded plugin: GUID={guid}, usage={usage}")
                else:
                    # Mod CSV 解析邏輯
                    csv_reader = csv.reader(lines)
                    next(csv_reader)  # 跳過標題行
                    header_row = next(csv_reader)  # 讀取欄位名稱行
                    header_map = {col.lower().strip(): idx for idx, col in enumerate(header_row)}
                    
                    for row in csv_reader:
                        if len(row) >= len(header_map):  # 確保行有足夠的列
                            try:
                                cleaned_row = {
                                    'GUID': row[header_map['guid']].strip(),
                                    'Cards with usages': row[header_map['cards with usages']].strip(),
                                    'Is installed': row[header_map['is installed']].strip(),
                                    'Filename': row[header_map['zipmod filename']].strip()
                                }
                                self.csv_file.append(cleaned_row)
                            except (IndexError, KeyError) as e:
                                print(f"Error processing row: {row}, Error: {str(e)}")
                                continue

            if not self.csv_file:
                raise ValueError(self.get_localized_text("error_no_data"))

            print(f"Loaded {len(self.csv_file)} items from CSV")
            for item in self.csv_file:
                print(f"Loaded item: {item}")

            self.update_ui_for_csv_type()
            self.drop_area.config(text=self.get_localized_text("success_csv_upload"))
                        
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            messagebox.showerror(
                self.get_localized_text("error_upload"),
                f"{self.get_localized_text('error_upload')}: {str(e)}"
            )



    def detect_low_usage_items(self):
        """檢測低使用量的項目"""
        if not self.validate_detection():
            return
                
        if self.csv_type is None:
            messagebox.showerror(
                self.get_localized_text("error_upload"),
                "No valid CSV type detected"
            )
            return

        try:
            self.low_usage_items = []
            min_usages = int(self.min_usages_var.get())
            usages = []
            low_usage_count = 0

            print(f"Detecting items with usage <= {min_usages}")
            
            for item in self.csv_file:
                try:
                    usage = int(item['Cards with usages'])
                    print(f"Checking item: GUID={item['GUID']}, usage={usage}")
                    usages.append(usage)
                    
                    if usage <= min_usages:
                        if self.csv_type == CSVType.PLUGIN:
                            guid = item['GUID'].strip()
                            if guid:
                                self.low_usage_items.append(guid)
                                print(f"Added low usage plugin: GUID={guid}, usage={usage}")
                                low_usage_count += 1
                        else:
                            filename = item['Filename']
                            if filename:
                                self.low_usage_items.append(filename)
                                print(f"Added low usage mod: Filename={filename}, usage={usage}")
                                low_usage_count += 1
                except (ValueError, KeyError) as e:
                    print(f"Error processing item: {item}, Error: {str(e)}")
                    continue

            print(f"Found {low_usage_count} items with low usage")
            print(f"Low usage items: {self.low_usage_items}")

            self.update_usage_range(usages)
            self.show_detection_results()
            self.detection_performed = True
                        
        except Exception as e:
            print(f"Error in detection: {str(e)}")
            messagebox.showerror(
                self.get_localized_text("error_upload"),
                f"Error during detection: {str(e)}"
            )

    def count_items_for_action(self, action):
            """計算可以執行指定操作的項目數量"""
            try:
                count = 0
                exclude_dir = self.get_target_folder_path()

                if self.csv_type == CSVType.PLUGIN:
                    print("Counting plugins...")
                    # custom模式下只檢查根目錄
                    if self.custom_mods_var.get():
                        for file in os.listdir(self.base_path):
                            if not os.path.isfile(os.path.join(self.base_path, file)):
                                continue
                            if not file.endswith(('.dll', '.dl_')):
                                continue
                            file_path = os.path.normpath(os.path.join(self.base_path, file))
                            if os.path.exists(file_path):
                                dll_guid = self.get_dll_guid(file_path)
                                if dll_guid in self.low_usage_items:
                                    count += 1
                                    print(f"Found matching plugin in root: {file_path} with GUID: {dll_guid}")
                    else:
                        # 遍歷所有子目錄，除了 low_usage_plugins
                        for root, file in self.walk_files(self.base_path, exclude_dir):
                            if file.endswith(('.dll', '.dl_')):
                                file_path = os.path.normpath(os.path.join(root, file))
                                if os.path.exists(file_path):
                                    dll_guid = self.get_dll_guid(file_path)
                                    if dll_guid in self.low_usage_items:
                                        count += 1
                                        print(f"Found matching plugin: {file_path} with GUID: {dll_guid}")
                else:
                    if self.custom_mods_var.get():
                        # 只檢查根目錄
                        files = os.listdir(self.base_path)
                        count = sum(1 for file in files if file in self.low_usage_items and 
                                os.path.isfile(os.path.join(self.base_path, file)))
                    else:
                        # 遍歷所有子目錄，除了 low_usage_mods
                        for root, file in self.walk_files(self.base_path, exclude_dir):
                            if file in self.low_usage_items:
                                count += 1
                
                print(f"Total items found: {count}")
                return count
            except Exception as e:
                print(f"Error in count_items_for_action: {str(e)}")
                return 0

    def handle_pack_action(self):
        """處理打包操作"""
        try:
            # 先計算有多少項目需要打包
            packable_count = self.count_items_for_action('pack')
            if packable_count == 0:
                nothing_key = "nothing_to_pack_plugin" if self.csv_type == CSVType.PLUGIN else "nothing_to_pack"
                messagebox.showinfo(
                    self.get_localized_text("nothing_to_pack_title"),
                    self.get_localized_text(nothing_key)
                )
                return

            # 只有在確實有項目需要打包時才建立資料夾
            print(f"Low usage items: {self.low_usage_items}")
            target_folder = self.get_target_folder_path()
            os.makedirs(target_folder, exist_ok=True)

            moved_count = self.move_items_to_folder(target_folder)
            print(f"Moved count: {moved_count}")
            
            if moved_count > 0:
                success_key = "success_pack_plugin" if self.csv_type == CSVType.PLUGIN else "success_pack"
                messagebox.showinfo(
                    self.get_localized_text("success_title"),
                    self.get_localized_text(success_key, moved_count)
                )
            else:
                # 如果最後沒有移動任何文件，刪除空資料夾
                self.clean_empty_folder(target_folder)
                nothing_key = "nothing_to_pack_plugin" if self.csv_type == CSVType.PLUGIN else "nothing_to_pack"
                messagebox.showinfo(
                    self.get_localized_text("nothing_to_pack_title"),
                    self.get_localized_text(nothing_key)
                )
                    
        except Exception as e:
            print(f"Error in handle_pack_action: {str(e)}")
            error_key = "error_pack_plugin" if self.csv_type == CSVType.PLUGIN else "error_pack"
            messagebox.showerror(
                self.get_localized_text("error_pack_title"),
                self.get_localized_text(error_key, str(e))
            )

    def move_items_to_folder(self, target_folder):
        """移動項目到指定資料夾"""
        try:
            moved_count = 0
            print(f"Moving files to {target_folder}")
            existing_moved = set(os.listdir(target_folder)) if os.path.exists(target_folder) else set()

            if self.csv_type == CSVType.PLUGIN:
                print("Processing plugin files")
                if self.custom_mods_var.get():
                    # 只檢查根目錄
                    for file in os.listdir(self.base_path):
                        if not os.path.isfile(os.path.join(self.base_path, file)):
                            continue
                        if not file.endswith(('.dll', '.dl_')):
                            continue
                        moved_count = self.process_plugin_file(file, self.base_path, target_folder, existing_moved, moved_count)
                else:
                    # 遍歷所有子目錄，除了 low_usage_plugins
                    for root, file in self.walk_files(self.base_path, target_folder):
                        if file.endswith(('.dll', '.dl_')):
                            moved_count = self.process_plugin_file(file, root, target_folder, existing_moved, moved_count)
            else:
                print("Processing mod files")
                if self.custom_mods_var.get():
                    # 只檢查根目錄的 mod 文件
                    for file in os.listdir(self.base_path):
                        if not os.path.isfile(os.path.join(self.base_path, file)):
                            continue
                        if file in self.low_usage_items:
                            moved_count = self.process_mod_file(file, self.base_path, target_folder, existing_moved, moved_count)
                else:
                    # 遍歷所有子目錄，除了 low_usage_mods
                    for root, file in self.walk_files(self.base_path, target_folder):
                        if file in self.low_usage_items:
                            moved_count = self.process_mod_file(file, root, target_folder, existing_moved, moved_count)

            print(f"Total moved: {moved_count}")
            return moved_count
        except Exception as e:
            print(f"Error moving files: {str(e)}")
            raise





    def get_dll_guid(self, dll_path):
        """從 DLL 文件中讀取 GUID（包括 .dll 和 .dl_ 文件）"""
        try:
            if dll_path.endswith('.dl_'):
                try:
                    guid = load_plugin_info(dll_path)  # 先嘗試直接讀取 .dl_
                    if guid:
                        return guid
                except Exception:
                    try:
                        # 如果直接讀取失敗，嘗試創建臨時 .dll 文件
                        temp_dll_path = dll_path + '.temp.dll'
                        shutil.copy2(dll_path, temp_dll_path)
                        guid = load_plugin_info(temp_dll_path)
                        os.remove(temp_dll_path)  # 清理臨時文件
                        if guid:
                            return guid
                    except Exception:
                        pass  # 如果臨時文件方法也失敗，繼續使用文件名方法
            else:
                # 一般 .dll 文件的處理
                guid = load_plugin_info(dll_path)
                if guid:
                    return guid
                    
            # 如果所有嘗試都失敗，使用文件名（不含副檔名）
            return os.path.splitext(os.path.basename(dll_path))[0]
            
        except Exception as e:
            print(f"Error reading GUID from {dll_path}: {str(e)}")
            # 發生錯誤時，返回文件名（不含副檔名）
            return os.path.splitext(os.path.basename(dll_path))[0]

    def process_plugin_file(self, file, root, target_folder, existing_moved, moved_count):
        """處理單個插件文件"""
        source_path = os.path.normpath(os.path.join(root, file))
        print(f"Checking file: {source_path}")
        
        if not os.path.exists(source_path):
            print(f"File not found: {source_path}")
            return moved_count
        
        if file in existing_moved:
            print(f"File already moved: {file}")
            return moved_count
        
        dll_guid = self.get_dll_guid(source_path)
        if dll_guid in self.low_usage_items:
            dest_path = os.path.normpath(os.path.join(target_folder, file))
            if not os.path.exists(dest_path):
                print(f"Moving {source_path} to {dest_path}")
                if self.safe_move_file(source_path, dest_path):
                    self.moved_files[dest_path] = source_path
                    moved_count += 1
        return moved_count

    def process_mod_file(self, file, root, target_folder, existing_moved, moved_count):
        """處理單個模組文件"""
        source_path = os.path.normpath(os.path.join(root, file))
        if os.path.isfile(source_path) and file not in existing_moved:
            dest_path = os.path.normpath(os.path.join(target_folder, file))
            if not os.path.exists(dest_path):
                print(f"Moving mod file: {source_path} to {dest_path}")
                if self.safe_move_file(source_path, dest_path):
                    self.moved_files[dest_path] = source_path
                    moved_count += 1
        return moved_count


    def handle_remove_action(self):
            """處理移除操作"""
            try:
                # 計算可移除的項目數量
                remove_count = self.count_items_for_action('remove')
                print(f"Items to remove: {remove_count}")

                if remove_count == 0:
                    nothing_key = "nothing_to_remove_plugin" if self.csv_type == CSVType.PLUGIN else "nothing_to_remove"
                    messagebox.showinfo(
                        self.get_localized_text("nothing_to_remove_title"),
                        self.get_localized_text(nothing_key)
                    )
                    return
                    
                # 確認移除操作
                confirm_key = "confirm_remove_plugin" if self.csv_type == CSVType.PLUGIN else "confirm_remove"
                if messagebox.askyesno(
                    self.get_localized_text("confirm_remove_title"),
                    self.get_localized_text(confirm_key, remove_count, int(self.min_usages_var.get()))
                ):
                    self.remove_low_usage_items()
            except Exception as e:
                print(f"Error in handle_remove_action: {str(e)}")
                error_key = "error_remove_plugin" if self.csv_type == CSVType.PLUGIN else "error_remove"
                messagebox.showerror(
                    self.get_localized_text("error_remove_title"),
                    self.get_localized_text(error_key, str(e))
                )

    def remove_low_usage_items(self):
        """移除低使用量的項目"""
        try:
            if not self.low_usage_items:
                nothing_key = "nothing_to_remove_plugin" if self.csv_type == CSVType.PLUGIN else "nothing_to_remove"
                messagebox.showinfo(
                    self.get_localized_text("nothing_to_remove_title"),
                    self.get_localized_text(nothing_key)
                )
                return

            print(f"Low usage items to remove: {self.low_usage_items}")
            removed_count = 0
            target_folder = self.get_target_folder_path()

            if self.csv_type == CSVType.PLUGIN:
                print("Processing plugin files for removal")
                if self.custom_mods_var.get():
                    # 只處理根目錄的文件
                    for file in os.listdir(self.base_path):
                        if not os.path.isfile(os.path.join(self.base_path, file)):
                            continue
                        if not file.endswith(('.dll', '.dl_')):
                            continue
                        removed_count = self.remove_plugin_file(file, self.base_path, removed_count)
                else:
                    # 遍歷所有子目錄，除了 low_usage_plugins
                    for root, file in self.walk_files(self.base_path, target_folder):
                        if file.endswith(('.dll', '.dl_')):
                            removed_count = self.remove_plugin_file(file, root, removed_count)
            else:
                if self.custom_mods_var.get():
                    # 只處理根目錄的文件
                    files = [f for f in os.listdir(self.base_path) 
                            if os.path.isfile(os.path.join(self.base_path, f))]
                    for file in files:
                        removed_count = self.remove_mod_file(file, self.base_path, removed_count)
                else:
                    # 遍歷所有子目錄，除了 low_usage_mods
                    for root, file in self.walk_files(self.base_path, target_folder):
                        removed_count = self.remove_mod_file(file, root, removed_count)

            # 顯示結果訊息
            if removed_count > 0:
                success_key = "success_remove_plugin" if self.csv_type == CSVType.PLUGIN else "success_remove"
                messagebox.showinfo(
                    self.get_localized_text("success_title"),
                    self.get_localized_text(success_key, removed_count)
                )
            else:
                nothing_key = "nothing_to_remove_plugin" if self.csv_type == CSVType.PLUGIN else "nothing_to_remove"
                messagebox.showinfo(
                    self.get_localized_text("nothing_to_remove_title"),
                    self.get_localized_text(nothing_key)
                )

        except Exception as e:
            print(f"Error in remove_low_usage_items: {str(e)}")
            error_key = "error_remove_plugin" if self.csv_type == CSVType.PLUGIN else "error_remove"
            messagebox.showerror(
                self.get_localized_text("error_remove_title"),
                self.get_localized_text(error_key, str(e))
            )

    def remove_plugin_file(self, file, root, removed_count):
            """處理單個插件文件的移除"""
            source_path = os.path.normpath(os.path.join(root, file))
            print(f"Checking file: {source_path}")
            
            if not os.path.exists(source_path):
                print(f"File not found: {source_path}")
                return removed_count
            
            dll_guid = self.get_dll_guid(source_path)
            print(f"File GUID: {dll_guid}")
            
            if dll_guid in self.low_usage_items:
                print(f"Removing file with matching GUID: {source_path}")
                if self.safe_remove_file(source_path):
                    removed_count += 1
                    print(f"Successfully removed: {source_path}")
            
            return removed_count

    def remove_mod_file(self, file, root, removed_count):
        """處理單個模組文件的移除"""
        if file in self.low_usage_items:
            mod_path = os.path.normpath(os.path.join(root, file))
            if os.path.isfile(mod_path):
                if self.safe_remove_file(mod_path):
                    removed_count += 1
                    print(f"Successfully removed mod: {mod_path}")
        return removed_count
    




    def execute_action(self):
        """執行選擇的操作（打包/移除/還原打包）"""
        if not self.validate_action():
            return
            
        try:
            # 根據選擇的操作執行相應的功能
            selected_action = self.action_combo.get()
            
            if selected_action == self.get_localized_text('action_pack'):
                print("Executing pack action")
                self.handle_pack_action()
                
            elif selected_action == self.get_localized_text('action_remove'):
                print("Executing remove action")
                self.handle_remove_action()
                
            elif selected_action == self.get_localized_text('action_undo_pack'):
                print("Executing undo pack action")
                self.undo_pack()
                
            else:
                print(f"Unknown action selected: {selected_action}")
                messagebox.showerror(
                    self.get_localized_text("error_upload"),
                    self.get_localized_text("error_unknown_action")
                )
                
        except Exception as e:
            print(f"Error executing action: {str(e)}")
            messagebox.showerror(
                self.get_localized_text("error_upload"),
                f"Error: {str(e)}"
            )

    def undo_pack(self):
        """復原打包操作"""
        try:
            if not self.moved_files:
                messagebox.showinfo(
                    self.get_localized_text("nothing_to_undo_title"),
                    self.get_localized_text("nothing_to_undo")
                )
                return

            target_folder = self.get_target_folder_path()
            if not os.path.exists(target_folder):
                messagebox.showinfo(
                    self.get_localized_text("nothing_to_undo_title"),
                    self.get_localized_text("nothing_to_undo")
                )
                return

            files_to_restore = []
            moved_files_copy = self.moved_files.copy()  # 創建副本以避免迭代時修改
            
            # 檢查需要還原的文件
            for dest_path, source_path in moved_files_copy.items():
                if os.path.exists(dest_path):
                    # 如果目標路徑存在源文件，跳過並移除記錄
                    if os.path.exists(source_path):
                        del self.moved_files[dest_path]
                        continue
                    files_to_restore.append((dest_path, source_path))

            if not files_to_restore:
                messagebox.showinfo(
                    self.get_localized_text("nothing_to_undo_title"),
                    self.get_localized_text("nothing_to_undo")
                )
                return

            # 執行還原
            restored_count = 0
            for dest_path, source_path in files_to_restore:
                try:
                    # 確保目標目錄存在
                    os.makedirs(os.path.dirname(source_path), exist_ok=True)
                    print(f"Restoring {dest_path} to {source_path}")
                    
                    # 移動文件
                    if self.safe_move_file(dest_path, source_path):
                        del self.moved_files[dest_path]
                        restored_count += 1
                        print(f"Successfully restored file to {source_path}")
                except Exception as e:
                    print(f"Error restoring file {dest_path}: {str(e)}")
                    continue

            if restored_count > 0:
                # 檢查並刪除空資料夾
                self.clean_empty_folder(target_folder)

                # 使用正確的成功訊息鍵值
                success_key = "success_undo_pack_plugin" if self.csv_type == CSVType.PLUGIN else "success_undo_pack"
                messagebox.showinfo(
                    self.get_localized_text("success_title"),
                    self.get_localized_text(success_key, restored_count)
                )

        except Exception as e:
            print(f"Error in undo_pack: {str(e)}")
            error_key = "error_undo_pack_plugin" if self.csv_type == CSVType.PLUGIN else "error_undo_pack"
            messagebox.showerror(
                self.get_localized_text("error_undo_pack_title"),
                self.get_localized_text(error_key, str(e))
            )

def main():
    root = tkdnd.Tk()
    app = KKCleanerTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()