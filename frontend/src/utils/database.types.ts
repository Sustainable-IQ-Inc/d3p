export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      climate_zones: {
        Row: {
          climate_zone_name: string | null
          created_at: string
          id: number
        }
        Insert: {
          climate_zone_name?: string | null
          created_at?: string
          id?: number
        }
        Update: {
          climate_zone_name?: string | null
          created_at?: string
          id?: number
        }
        Relationships: []
      }
      companies: {
        Row: {
          company_domain: string | null
          company_name: string | null
          created_at: string
          id: number
        }
        Insert: {
          company_domain?: string | null
          company_name?: string | null
          created_at?: string
          id?: number
        }
        Update: {
          company_domain?: string | null
          company_name?: string | null
          created_at?: string
          id?: number
        }
        Relationships: []
      }
      eeu_data: {
        Row: {
          "active (from record_id)": string | null
          active_bulk: string | null
          area_units: string | null
          "Baseline BEM Report (from record_id)": string | null
          climate_zone: string | null
          company_id: number | null
          company_id_bulk: string | null
          Cooling_DistrictHeating: string | null
          Cooling_Electricity: string | null
          Cooling_Other: string | null
          created: string | null
          DHW_DistrictHeating: string | null
          DHW_Electricity: string | null
          DHW_NaturalGas: string | null
          DHW_Other: string | null
          energy_code_bulk: string | null
          energy_units: string | null
          "Exterior Lighting_Electricity": string | null
          ExteriorUsage_Electricity: string | null
          ExteriorUsage_NaturalGas: string | null
          Fans_Electricity: string | null
          file_type: string | null
          filename: string | null
          "Heat Rejection_Electricity": string | null
          Heating_DistrictHeating: string | null
          Heating_Electricity: string | null
          Heating_NaturalGas: string | null
          Heating_Other: string | null
          HeatRecovery_Electricity: string | null
          HeatRecovery_Other: string | null
          Humidification_Electricity: string | null
          id: number
          "Interior Lighting_Electricity": string | null
          "Other_On-SiteRenewables": string | null
          OtherEndUse_Electricity: string | null
          OtherEndUse_NaturalGas: string | null
          OtherEndUse_Other: string | null
          phase: string | null
          phase_bulk: string | null
          "Plug Loads_Electricity": string | null
          "Process Refrigeration_Electricity": string | null
          project_id: number | null
          project_id_bulk: string | null
          project_name: string | null
          project_rec_id: string | null
          Pumps_Electricity: string | null
          Pumps_NaturalGas: string | null
          report_type: string | null
          "SolarDHW_On-SiteRenewables": string | null
          "SolarPV_On-SiteRenewables": string | null
          total_DistrictHeating: string | null
          total_Electricity: string | null
          total_energy: string | null
          total_NaturalGas: string | null
          "total_On-SiteRenewables": string | null
          total_Other: string | null
          "Use Type": string | null
          use_type_bulk: string | null
          use_type_total_area: string | null
          valid_output: boolean | null
          weather_station: string | null
          weather_string: string | null
          "Wind_On-SiteRenewables": string | null
        }
        Insert: {
          "active (from record_id)"?: string | null
          active_bulk?: string | null
          area_units?: string | null
          "Baseline BEM Report (from record_id)"?: string | null
          climate_zone?: string | null
          company_id?: number | null
          company_id_bulk?: string | null
          Cooling_DistrictHeating?: string | null
          Cooling_Electricity?: string | null
          Cooling_Other?: string | null
          created?: string | null
          DHW_DistrictHeating?: string | null
          DHW_Electricity?: string | null
          DHW_NaturalGas?: string | null
          DHW_Other?: string | null
          energy_code_bulk?: string | null
          energy_units?: string | null
          "Exterior Lighting_Electricity"?: string | null
          ExteriorUsage_Electricity?: string | null
          ExteriorUsage_NaturalGas?: string | null
          Fans_Electricity?: string | null
          file_type?: string | null
          filename?: string | null
          "Heat Rejection_Electricity"?: string | null
          Heating_DistrictHeating?: string | null
          Heating_Electricity?: string | null
          Heating_NaturalGas?: string | null
          Heating_Other?: string | null
          HeatRecovery_Electricity?: string | null
          HeatRecovery_Other?: string | null
          Humidification_Electricity?: string | null
          id: number
          "Interior Lighting_Electricity"?: string | null
          "Other_On-SiteRenewables"?: string | null
          OtherEndUse_Electricity?: string | null
          OtherEndUse_NaturalGas?: string | null
          OtherEndUse_Other?: string | null
          phase?: string | null
          phase_bulk?: string | null
          "Plug Loads_Electricity"?: string | null
          "Process Refrigeration_Electricity"?: string | null
          project_id?: number | null
          project_id_bulk?: string | null
          project_name?: string | null
          project_rec_id?: string | null
          Pumps_Electricity?: string | null
          Pumps_NaturalGas?: string | null
          report_type?: string | null
          "SolarDHW_On-SiteRenewables"?: string | null
          "SolarPV_On-SiteRenewables"?: string | null
          total_DistrictHeating?: string | null
          total_Electricity?: string | null
          total_energy?: string | null
          total_NaturalGas?: string | null
          "total_On-SiteRenewables"?: string | null
          total_Other?: string | null
          "Use Type"?: string | null
          use_type_bulk?: string | null
          use_type_total_area?: string | null
          valid_output?: boolean | null
          weather_station?: string | null
          weather_string?: string | null
          "Wind_On-SiteRenewables"?: string | null
        }
        Update: {
          "active (from record_id)"?: string | null
          active_bulk?: string | null
          area_units?: string | null
          "Baseline BEM Report (from record_id)"?: string | null
          climate_zone?: string | null
          company_id?: number | null
          company_id_bulk?: string | null
          Cooling_DistrictHeating?: string | null
          Cooling_Electricity?: string | null
          Cooling_Other?: string | null
          created?: string | null
          DHW_DistrictHeating?: string | null
          DHW_Electricity?: string | null
          DHW_NaturalGas?: string | null
          DHW_Other?: string | null
          energy_code_bulk?: string | null
          energy_units?: string | null
          "Exterior Lighting_Electricity"?: string | null
          ExteriorUsage_Electricity?: string | null
          ExteriorUsage_NaturalGas?: string | null
          Fans_Electricity?: string | null
          file_type?: string | null
          filename?: string | null
          "Heat Rejection_Electricity"?: string | null
          Heating_DistrictHeating?: string | null
          Heating_Electricity?: string | null
          Heating_NaturalGas?: string | null
          Heating_Other?: string | null
          HeatRecovery_Electricity?: string | null
          HeatRecovery_Other?: string | null
          Humidification_Electricity?: string | null
          id?: number
          "Interior Lighting_Electricity"?: string | null
          "Other_On-SiteRenewables"?: string | null
          OtherEndUse_Electricity?: string | null
          OtherEndUse_NaturalGas?: string | null
          OtherEndUse_Other?: string | null
          phase?: string | null
          phase_bulk?: string | null
          "Plug Loads_Electricity"?: string | null
          "Process Refrigeration_Electricity"?: string | null
          project_id?: number | null
          project_id_bulk?: string | null
          project_name?: string | null
          project_rec_id?: string | null
          Pumps_Electricity?: string | null
          Pumps_NaturalGas?: string | null
          report_type?: string | null
          "SolarDHW_On-SiteRenewables"?: string | null
          "SolarPV_On-SiteRenewables"?: string | null
          total_DistrictHeating?: string | null
          total_Electricity?: string | null
          total_energy?: string | null
          total_NaturalGas?: string | null
          "total_On-SiteRenewables"?: string | null
          total_Other?: string | null
          "Use Type"?: string | null
          use_type_bulk?: string | null
          use_type_total_area?: string | null
          valid_output?: boolean | null
          weather_station?: string | null
          weather_string?: string | null
          "Wind_On-SiteRenewables"?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "eeu_data_company_id_fkey"
            columns: ["company_id"]
            isOneToOne: false
            referencedRelation: "companies"
            referencedColumns: ["id"]
          }
        ]
      }
      energy_codes: {
        Row: {
          created_at: string
          energy_code_name: string | null
          id: number
        }
        Insert: {
          created_at?: string
          energy_code_name?: string | null
          id?: number
        }
        Update: {
          created_at?: string
          energy_code_name?: string | null
          id?: number
        }
        Relationships: []
      }
      project_construction_categories: {
        Row: {
          created_at: string
          id: number
          project_construction_category_id: string | null
        }
        Insert: {
          created_at?: string
          id?: number
          project_construction_category_id?: string | null
        }
        Update: {
          created_at?: string
          id?: number
          project_construction_category_id?: string | null
        }
        Relationships: []
      }
      project_phases: {
        Row: {
          created_at: string
          id: number
        }
        Insert: {
          created_at?: string
          id?: number
        }
        Update: {
          created_at?: string
          id?: number
        }
        Relationships: []
      }
      project_use_types: {
        Row: {
          created_at: string
          id: number
          project_use_type_name: string | null
        }
        Insert: {
          created_at?: string
          id?: number
          project_use_type_name?: string | null
        }
        Update: {
          created_at?: string
          id?: number
          project_use_type_name?: string | null
        }
        Relationships: []
      }
      projects: {
        Row: {
          created_at: string
          id: number
          id_uuid: string
          project_name: string | null
          custom_project_id: string | null
        }
        Insert: {
          created_at?: string
          id?: number
          id_uuid: string
          project_name?: string | null
          custom_project_id?: string | null
        }
        Update: {
          created_at?: string
          id?: number
          id_uuid?: string
          project_name?: string | null
          custom_project_id?: string | null
        }
        Relationships: []
      }
      report_types: {
        Row: {
          created_at: string
          id: number
          report_type_name: string | null
        }
        Insert: {
          created_at?: string
          id?: number
          report_type_name?: string | null
        }
        Update: {
          created_at?: string
          id?: number
          report_type_name?: string | null
        }
        Relationships: []
      }
      upload_statuses: {
        Row: {
          created_at: string
          id: number
          status: string | null
        }
        Insert: {
          created_at?: string
          id?: number
          status?: string | null
        }
        Update: {
          created_at?: string
          id?: number
          status?: string | null
        }
        Relationships: []
      }
      uploads_single: {
        Row: {
          area: number | null
          area_units: string | null
          baseline_file_url: string | null
          climate_zone_id: number | null
          climate_zone_str: string | null
          created_at: string
          design_file_url: string | null
          id: number
          project_name: string | null
          project_phase_id: number | null
          project_use_case_id: number | null
          user_id: number | null
        }
        Insert: {
          area?: number | null
          area_units?: string | null
          baseline_file_url?: string | null
          climate_zone_id?: number | null
          climate_zone_str?: string | null
          created_at?: string
          design_file_url?: string | null
          id?: number
          project_name?: string | null
          project_phase_id?: number | null
          project_use_case_id?: number | null
          user_id?: number | null
        }
        Update: {
          area?: number | null
          area_units?: string | null
          baseline_file_url?: string | null
          climate_zone_id?: number | null
          climate_zone_str?: string | null
          created_at?: string
          design_file_url?: string | null
          id?: number
          project_name?: string | null
          project_phase_id?: number | null
          project_use_case_id?: number | null
          user_id?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "uploads_single_climate_zone_id_fkey"
            columns: ["climate_zone_id"]
            isOneToOne: false
            referencedRelation: "climate_zones"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "uploads_single_project_use_case_id_fkey"
            columns: ["project_use_case_id"]
            isOneToOne: false
            referencedRelation: "project_use_types"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "uploads_single_user_id_fkey"
            columns: ["user_id"]
            isOneToOne: false
            referencedRelation: "users"
            referencedColumns: ["id"]
          }
        ]
      }
      users: {
        Row: {
          company_id: number | null
          created_at: string
          id: number
          user_email: string | null
          user_first: string | null
          user_last: string | null
        }
        Insert: {
          company_id?: number | null
          created_at?: string
          id?: number
          user_email?: string | null
          user_first?: string | null
          user_last?: string | null
        }
        Update: {
          company_id?: number | null
          created_at?: string
          id?: number
          user_email?: string | null
          user_first?: string | null
          user_last?: string | null
        }
        Relationships: []
      }
      views: {
        Row: {
          created_at: string
          id: number
          name: string | null
        }
        Insert: {
          created_at?: string
          id?: number
          name?: string | null
        }
        Update: {
          created_at?: string
          id?: number
          name?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

export type Tables<
  PublicTableNameOrOptions extends
    | keyof (Database["public"]["Tables"] & Database["public"]["Views"])
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof (Database[PublicTableNameOrOptions["schema"]]["Tables"] &
        Database[PublicTableNameOrOptions["schema"]]["Views"])
    : never = never
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? (Database[PublicTableNameOrOptions["schema"]]["Tables"] &
      Database[PublicTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : PublicTableNameOrOptions extends keyof (Database["public"]["Tables"] &
      Database["public"]["Views"])
  ? (Database["public"]["Tables"] &
      Database["public"]["Views"])[PublicTableNameOrOptions] extends {
      Row: infer R
    }
    ? R
    : never
  : never

export type TablesInsert<
  PublicTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicTableNameOrOptions["schema"]]["Tables"]
    : never = never
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? Database[PublicTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : PublicTableNameOrOptions extends keyof Database["public"]["Tables"]
  ? Database["public"]["Tables"][PublicTableNameOrOptions] extends {
      Insert: infer I
    }
    ? I
    : never
  : never

export type TablesUpdate<
  PublicTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Database },
  TableName extends PublicTableNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicTableNameOrOptions["schema"]]["Tables"]
    : never = never
> = PublicTableNameOrOptions extends { schema: keyof Database }
  ? Database[PublicTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : PublicTableNameOrOptions extends keyof Database["public"]["Tables"]
  ? Database["public"]["Tables"][PublicTableNameOrOptions] extends {
      Update: infer U
    }
    ? U
    : never
  : never

export type Enums<
  PublicEnumNameOrOptions extends
    | keyof Database["public"]["Enums"]
    | { schema: keyof Database },
  EnumName extends PublicEnumNameOrOptions extends { schema: keyof Database }
    ? keyof Database[PublicEnumNameOrOptions["schema"]]["Enums"]
    : never = never
> = PublicEnumNameOrOptions extends { schema: keyof Database }
  ? Database[PublicEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : PublicEnumNameOrOptions extends keyof Database["public"]["Enums"]
  ? Database["public"]["Enums"][PublicEnumNameOrOptions]
  : never
