export interface SubmitUploadProps {
    project_use_type_id: number;
    project_phase_id: number;
    project_construction_category_id: number;
    baseline_url?: string;
    design_url?: string;
    project_id: string;
    energy_code_id: number;
    report_type_id?: number;
    baseline_eeu_id?: number| null;
    design_eeu_id: number;
    year: number;
    reporting_year: number;
    use_type_subtype_id?: number | null;  }