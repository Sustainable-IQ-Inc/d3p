import { useState, useEffect } from 'react';
import useSupabase from 'hooks/useSupabase';

interface UserProps {
  id: string; // Added id field
  name: string;
  email: string;
  avatar: string;
  thumb: string;
  company: string;
  role: string;
  companyId: string;
}

const useUser = () => {
  const supabase = useSupabase();
  const [loading, setLoading] = useState(true);
  const [userEmail, setUserEmail] = useState('');
  const [companyId, setCompanyId] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [userRole, setUserRole] = useState('');
  const [userId, setUserId] = useState(''); // Added state for userId

  useEffect(() => {
    const fetchUser = async () => {
      const data = await supabase.auth.getUser();
      if (data) {
        setUserId(data.data.user?.id || ''); // Set userId
        setUserEmail(data.data.user?.email || '');
        setCompanyId(data.data.user?.user_metadata.company_id || '');
        setUserRole(data.data.user?.user_metadata.role || '');

        const { data: company, error } = await supabase
          .from('companies')
          .select('company_name')
          .eq('id', data.data.user?.user_metadata.company_id)
          .single();

        if (error) {
          console.error('Error fetching company: ', error);
        } else if (company) {
          setCompanyName(company.company_name);
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, [supabase]);

  const image = '/assets/images/users/avatar-1.png';
  const thumb = '/assets/images/users/avatar-thumb-1.png';

  const newUser: UserProps = {
    id: userId, // Added id field
    name: userEmail,
    email: userEmail,
    avatar: image,
    thumb,
    company: companyName,
    role: userRole,
    companyId: companyId,
  };

  return { user: newUser, loading };
};

export default useUser;