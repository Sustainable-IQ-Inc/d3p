import axios from 'axios';
import {  createClient} from 'utils/supabase';
interface CreateCompanyProps {
    company_name: string
}

const createCompany = async ({ companyProps }: {companyProps: CreateCompanyProps}): Promise<string> => {
    const supabase = createClient();
    const { data: session } = await supabase.auth.getSession();
    try {
        const response = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE_URL}/create_company/`, {
            ...companyProps
        },
        {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${session?.session?.access_token}`
            }
        });

        if (response.data === 'success') {
            return 'success';
        } else {
            return 'failed';
        }
    } catch (error) {
        console.error('Error creating project:', error);
        return 'failed';
    }
};

export default createCompany;