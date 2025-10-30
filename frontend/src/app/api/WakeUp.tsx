import { createClient } from "utils/supabase";

export const wakeUpApi = async () => {
  const supabase = createClient();
  const { data: session } = await supabase.auth.getSession();
  let url = `${process.env.NEXT_PUBLIC_API_BASE_URL}/wake-up/`;
  try {
    await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${session?.session?.access_token}`,
      },
    });
  } catch (error) {
    console.error("Failed to wake up API:", error);
  }
};
