
export interface Gazette {
  gazette_id: string;
  published_date: string;
  parent_gazette_id?: string;
}

export interface GazetteDetail {
  gazette_id: string;
  published_date: string;
  minister: string;
  departments: string[];
  laws: string[];
  functions: string[];
}

export interface Amendment {
  gazette_id: string;
  published_date: string;
  parent_gazette_id?: string;
}

export interface GraphNode {
  id: string;
  label: string;
  kind: 'base' | 'amendment' | 'minister' | 'department' | 'law';
  published_date?: string;
  parent_gazette_id?: string;
  type?: string;
  is_base?: boolean;
}

export interface GraphLink {
  source: string;
  target: string;
  kind: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export interface Entity {
  id: string;
  type: 'gazette' | 'minister' | 'department' | 'law' | 'unknown';
  name: string;
  published_date?: string;
}

export interface Relationship {
  type: string;
  properties: Record<string, any>;
}

export interface GazetteFullDetails {
  gazette: {
    gazette_id: string;
    published_date?: string;
    parent_gazette_id?: string;
    type: 'base' | 'amendment';
  };
  entities: Entity[];
  relationships: Relationship[];
}
