"use client";

import React from "react";

import { createClient } from "utils/supabase";

export default async function StreamlitComponent() {
  const supabase = createClient();

  const { data } = await supabase.auth.getSession();

  const url = `${process.env.NEXT_PUBLIC_STREAMLIT_URL}/?token=${data.session?.access_token}`;

  return (
    <iframe
      src={url} // replace with your Streamlit app's url
      width="100%"
      height="800px"
      style={{ border: "none" }}
    />
  );
}
