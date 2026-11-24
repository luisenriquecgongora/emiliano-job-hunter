// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use tauri::Manager;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ApplicationRecord {
    pub id: String,
    pub company: String,
    pub role: String,
    #[serde(rename = "cvVariant")]
    pub cv_variant: String,
    pub stage: String,
    #[serde(rename = "fitScore")]
    pub fit_score: u32,
    pub compensation: String,
    pub portal: String,
    pub location: String,
    #[serde(rename = "dateApplied")]
    pub date_applied: String,
    pub pitch: String,
    #[serde(rename = "rodoAttached")]
    pub rodo_attached: bool,
}

#[tauri::command]
fn get_applications() -> Result<Vec<ApplicationRecord>, String> {
    let path = PathBuf::from("data/applications_crm.json");
    if path.exists() {
        let content = fs::read_to_string(&path).map_err(|e| e.to_string())?;
        let records: Vec<ApplicationRecord> = serde_json::from_str(&content).map_err(|e| e.to_string())?;
        Ok(records)
    } else {
        Ok(vec![])
    }
}

#[tauri::command]
fn save_applications(applications: Vec<ApplicationRecord>) -> Result<bool, String> {
    let path = PathBuf::from("data/applications_crm.json");
    let json = serde_json::to_string_pretty(&applications).map_err(|e| e.to_string())?;
    fs::write(&path, json).map_err(|e| e.to_string())?;
    Ok(true)
}

fn main() {
    // Isolate WebView2 data directory to prevent HRESULT 0x800700AA collisions
    let app_data = std::env::var("LOCALAPPDATA").unwrap_or_else(|_| ".".into());
    let webview_dir = PathBuf::from(app_data).join("EmilianoJobHunter_WebView");
    let _ = fs::create_dir_all(&webview_dir);
    std::env::set_var("WEBVIEW2_USER_DATA_FOLDER", &webview_dir);

    println!("[JobHunter] Initializing Tauri Builder with isolated WebView2 dir: {:?}", webview_dir);

    let app = tauri::Builder::default()
        .setup(|app| {
            println!("[JobHunter Setup] Hook started.");
            if let Some(win) = app.get_webview_window("main") {
                println!("[JobHunter Setup] Found window 'main'. Ensuring visibility and focus...");
                let _ = win.show();
                let _ = win.unminimize();
                let _ = win.set_focus();
                let hwnd_debug = format!("{:?}", win.hwnd());
                println!("[JobHunter Setup] Main window HWND = {}", hwnd_debug);
                let _ = fs::write("C:\\Users\\artlu\\OracliomNew\\Oracliom\\scratch\\hunter_hwnd.txt", &hwnd_debug);
                println!("[JobHunter Setup] Main window showed successfully!");
            } else {
                eprintln!("[JobHunter Setup] Warning: window 'main' not returned by get_webview_window!");
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_applications,
            save_applications
        ])
        .build(tauri::generate_context!())
        .expect("error while building Emiliano Job Hunter Tauri application");

    app.run(|_app_handle, event| {
        match &event {
            tauri::RunEvent::MainEventsCleared => {},
            _ => println!("[JobHunter Event] {:?}", event),
        }
    });
}
