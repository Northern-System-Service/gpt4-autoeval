/**
 * Google Apps Script
 * ELYZA-tasks-100 の評価結果取り込みスクリプト
 * 
 * Google Drive に保存した ELYZA-tasks-100 の評価結果 (preds.json [LLMの回答] および result.json [GPT-4による評価]) を、
 * スプレッドシートに取り込む。
 * 
 * Changelog:
 * 2023-12-11 新規作成
 * 2023-12-20 コメントの追加
 * 2024-04-23 開始列を修正（CZ->E）
 */

/**
 * メイン関数。
 * 指定されたフォルダパスからファイルを検索し、スプレッドシートにデータを取り込む。
 */
function main() {
  var folderPath = 'llm_research/migration'; // クロールするフォルダのパス
  var startRow = 3; // 開始行
  var startColumnLetter = "E"; // 開始列
  var startColumn = columnToNumber(startColumnLetter);
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet(); // アクティブなシートを取得

  crawlFolder(folderPath, startRow, startColumn, sheet);
}

/**
 * 指定されたパスにあるフォルダをクロールし、processFolder で定義した処理を行う。
 * 
 * @param {string} path - クロールするフォルダのパス。
 * @param {number} startRow - スプレッドシートに書き込む開始行。
 * @param {number} startColumn - スプレッドシートに書き込む開始列。
 * @param {Object} sheet - 操作するスプレッドシートのシートオブジェクト。
 */
function crawlFolder(path, startRow, startColumn, sheet) {
  // 引数で与えられたパスを '/' で分割し、フォルダの階層を取得
  var folders = path.split('/');
  var currentFolder = DriveApp.getRootFolder();

  // パスの各階層に対してループを行い、目的のフォルダを探索
  folders.forEach(function(folderName) {
    var nextFolders = currentFolder.getFoldersByName(folderName);

    // フォルダが見つからない場合はエラー
    if (!nextFolders.hasNext()) {
      throw new Error('Folder not found: ' + folderName);
    }

    // 次の階層のフォルダを現在のフォルダとする
    currentFolder = nextFolders.next();
  });

  // 目的のフォルダを見つけたら、そのフォルダ内の処理を行う関数を呼び出す
  processFolder(currentFolder, startRow, startColumn, sheet);
}

/**
 * 指定されたフォルダ内のファイルを処理し、スプレッドシートにデータを取り込む。
 * 
 * @param {Object} folder - 処理するフォルダのオブジェクト。
 * @param {number} startRow - スプレッドシートに書き込む開始行。
 * @param {number} startColumn - スプレッドシートに書き込む開始列。
 * @param {Object} sheet - 操作するスプレッドシートのシートオブジェクト。
 */
function processFolder(folder, startRow, startColumn, sheet) {
  // フォルダと行、列、シート情報をログ出力
  console.log(`processFolder: ${folder}, ${startRow}, ${startColumn}, ${sheet}`);

  // フォルダ内の全ファイルを取得
  var files = folder.getFiles();
  var predsFileId = '';
  var resultFileId = '';

  // ファイルのイテレーションを行い、必要なファイルIDを取得
  while (files.hasNext()) {
    var file = files.next();
    var fileName = file.getName();
    if (fileName === 'preds.jsonl') {
      predsFileId = file.getId();
    } else if (fileName === 'result.jsonl') {
      resultFileId = file.getId();
    }
  }

  // 必要なファイルが見つかった場合...
  if (predsFileId && resultFileId) {
    // 見つかったファイルの情報をログ出力
    console.log(`processFolder: Found relevant files ${predsFileId}, ${resultFileId}`);

    // スプレッドシートにヘッダを設定
    setHeaders(folder, startRow, startColumn, sheet);

    // ファイルから内容を読み込み、文字列として取得
    var predsContent = DriveApp.getFileById(predsFileId).getBlob().getDataAsString();
    var resultContent = DriveApp.getFileById(resultFileId).getBlob().getDataAsString();
    var predsLines = predsContent.split('\n');
    var resultLines = resultContent.split('\n');

    console.log(`processFolder: preds has ${predsLines.length} lines, result has ${resultLines.length} lines`);

    // LLM の回答、GPT-4 の評価理由、GPT-4 の最終評価を追加
    for (var i = 0; i < Math.max(predsLines.length, resultLines.length); i++) {
      var predsData = predsLines[i] ? JSON.parse(predsLines[i]) : {};
      var resultData = resultLines[i] ? JSON.parse(resultLines[i]) : {};
      var row = startRow + i;
      sheet.getRange(row, startColumn).setValue(predsData.pred || '');
      sheet.getRange(row, startColumn + 1).setValue(resultData.reason || '');
      sheet.getRange(row, startColumn + 2).setValue(resultData.grade || '');
    }

    // 次のフォルダ用に列をシフト
    startColumn += 3; 
    console.log(`processFolder: startColumn is now ${startColumn}`);
  }

  // サブフォルダに対する処理
  var subFolders = folder.getFolders();
  while (subFolders.hasNext()) {
    var subFolder = subFolders.next();
    startColumn = processFolder(subFolder, startRow, startColumn, sheet);
  }

  // 処理された最終列を返す
  return startColumn;
}

/**
 * 指定されたフォルダのヘッダー情報をスプレッドシートに設定する。
 * 
 * @param {Object} folder - ヘッダーを設定するフォルダのオブジェクト。
 * @param {number} startRow - スプレッドシートに書き込む開始行。
 * @param {number} startColumn - スプレッドシートに書き込む開始列。
 * @param {Object} sheet - 操作するスプレッドシートのシートオブジェクト。
 */
function setHeaders(folder, startRow, startColumn, sheet) {
  // フォルダの名前と親ディレクトリの名前を取得
  var folderName = folder.getName();
  var parentName = '';
  var parents = folder.getParents();
  if (parents.hasNext()) {
    parentName = parents.next().getName();
  }

  // ヘッダを編集
  var headerPrefix = parentName + '/' + folderName;
  sheet.getRange(startRow - 2, startColumn).setValue(headerPrefix + '\n回答');
  sheet.getRange(startRow - 2, startColumn + 1).setValue(headerPrefix + '\n講評 (GPT-4)');
  sheet.getRange(startRow - 2, startColumn + 2).setValue(headerPrefix + '\n採点結果 (GPT-4)');
}

/**
 * 列表記（A, B, ..., Z, AA, AB, ...）を列番号（1, 2, ..., 26, 27, 28, ...）に変換する
 */
function columnToNumber(column) {
  var column = column.toUpperCase(); // 大文字に変換
  var length = column.length;
  var number = 0;

  for (var i = 0; i < length; i++) {
    number *= 26;
    number += (column.charCodeAt(i) - 'A'.charCodeAt(0) + 1);
  }

  return number;
}
