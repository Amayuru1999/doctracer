
export interface Gazette {
  gazette_id: string;
  published_date: string;
}

export interface GazetteDetail {
  gazette_id: string;
  published_date: string;
  minister: string;
  departments: string[];
  laws: string[];
  functions: string[];
}
