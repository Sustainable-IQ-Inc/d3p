"use client";

import { createClient } from "utils/supabase";

export async function getProjectDetailsEndUsesChart(
  projectId: string,
  baseline_design: string,
  measurementSystem?: string
) {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();

  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/project_energy_end_uses/`;
  let params = new URLSearchParams();

  if (projectId !== undefined) {
    params.append("project_id", String(projectId));
  }
  if (baseline_design) {
    params.append("baseline_design", baseline_design);
  }
  if (measurementSystem) {
    params.append("measurement_system", measurementSystem);
  }

  if (params.toString()) {
    url += `?${params.toString()}`;
  }

  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${session?.session?.access_token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch project details end uses chart');
  }

  const data = await response.json();
  return data;
}

