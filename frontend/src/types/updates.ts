export interface ProjectUpdate {
    project_id: string;
    energy_code_id?: string;
    project_construction_category_id?: string;
    project_phase_id?: string;
    project_use_type_id?: string;
    year?: number;
    reporting_year?: number;
    user_id?: string;
    custom_project_id?: string;
    ddx_override_use_type_total_area_sf?: string;
    use_type_total_area?: string;
}

export interface EEUUpdate {
    project_id?: string;
    use_type_total_area?: string;
    climate_zone?: string;
    zip_code?: string;
    city?: string;
    state?: string;
    new_value?: string;
    cell_key?: string;
    eeu_id?: number;
    current_units?: string;
}

export interface UploadUpdate {
    project_id: string;
    use_type_total_area?: string;
    user_id?: string;
}