// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

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
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            get_applications,
            save_applications
        ])
        .run(tauri::generate_context!())
        .expect("error while running Emiliano Job Hunter Tauri application");
}
