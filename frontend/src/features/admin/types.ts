export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: string;
  facility_id: number;
  is_active: boolean;
  profession: string | null;
  license_number: string | null;
}

export interface AdminFacility {
  id: number;
  name: string;
  code: string;
  facility_type: string;
  address: string | null;
  province_code: string | null;
  regency_code: string | null;
  subdistrict_code: string | null;
  is_active: boolean;
}

export interface AdminUserListResponse {
  items: AdminUser[];
}

export interface AdminFacilityListResponse {
  items: AdminFacility[];
}
