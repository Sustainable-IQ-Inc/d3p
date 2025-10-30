import { useMemo } from 'react';
import { createClient } from 'utils/supabase';
 
function useSupabase() {
  return useMemo(createClient, []);
}
 
export default useSupabase;