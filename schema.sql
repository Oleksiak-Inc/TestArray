--
-- PostgreSQL database dump
--

-- Dumped from database version 16.14 (Debian 16.14-1.pgdg13+1)
-- Dumped by pg_dump version 16.14 (Debian 16.14-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO admin;

--
-- Name: attachments; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.attachments (
    id integer NOT NULL,
    parent_attachment_id integer,
    uploaded_by integer NOT NULL,
    edited_by integer,
    filename character varying,
    relative_path character varying,
    uploaded_at timestamp with time zone DEFAULT now(),
    edited_at timestamp with time zone
);


ALTER TABLE public.attachments OWNER TO admin;

--
-- Name: attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.attachments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attachments_id_seq OWNER TO admin;

--
-- Name: attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.attachments_id_seq OWNED BY public.attachments.id;


--
-- Name: clients; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.clients (
    id integer NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.clients OWNER TO admin;

--
-- Name: clients_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.clients_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.clients_id_seq OWNER TO admin;

--
-- Name: clients_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.clients_id_seq OWNED BY public.clients.id;


--
-- Name: devices; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.devices (
    id integer NOT NULL,
    project_id integer NOT NULL,
    name_external character varying,
    name_internal character varying,
    cpu character varying,
    gpu character varying,
    ram character varying
);


ALTER TABLE public.devices OWNER TO admin;

--
-- Name: devices_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.devices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.devices_id_seq OWNER TO admin;

--
-- Name: devices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.devices_id_seq OWNED BY public.devices.id;


--
-- Name: executions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.executions (
    id integer NOT NULL,
    device_id integer NOT NULL,
    run_id integer NOT NULL,
    test_case_version_id integer NOT NULL,
    executed_by integer,
    status_id integer,
    attachment_id integer,
    resolution_id integer,
    actual_result text,
    executed_at timestamp with time zone,
    execution_order integer NOT NULL
);


ALTER TABLE public.executions OWNER TO admin;

--
-- Name: executions_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.executions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.executions_id_seq OWNER TO admin;

--
-- Name: executions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.executions_id_seq OWNED BY public.executions.id;


--
-- Name: projects; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.projects (
    id integer NOT NULL,
    name character varying,
    client_id integer NOT NULL
);


ALTER TABLE public.projects OWNER TO admin;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.projects_id_seq OWNER TO admin;

--
-- Name: projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;


--
-- Name: resolutions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resolutions (
    id integer NOT NULL,
    h integer NOT NULL,
    w integer NOT NULL
);


ALTER TABLE public.resolutions OWNER TO admin;

--
-- Name: resolutions_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.resolutions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resolutions_id_seq OWNER TO admin;

--
-- Name: resolutions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.resolutions_id_seq OWNED BY public.resolutions.id;


--
-- Name: runs; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.runs (
    id integer NOT NULL,
    name character varying,
    started_at timestamp with time zone,
    done_at timestamp with time zone,
    test_suite_metadata text,
    project_id integer NOT NULL
);


ALTER TABLE public.runs OWNER TO admin;

--
-- Name: runs_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.runs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.runs_id_seq OWNER TO admin;

--
-- Name: runs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.runs_id_seq OWNED BY public.runs.id;


--
-- Name: scenarios; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.scenarios (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.scenarios OWNER TO admin;

--
-- Name: scenarios_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.scenarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scenarios_id_seq OWNER TO admin;

--
-- Name: scenarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.scenarios_id_seq OWNED BY public.scenarios.id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.sessions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL
);


ALTER TABLE public.sessions OWNER TO admin;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sessions_id_seq OWNER TO admin;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.id;


--
-- Name: status_sets; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.status_sets (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.status_sets OWNER TO admin;

--
-- Name: status_sets_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.status_sets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_sets_id_seq OWNER TO admin;

--
-- Name: status_sets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.status_sets_id_seq OWNED BY public.status_sets.id;


--
-- Name: statuses; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.statuses (
    id integer NOT NULL,
    status_set_id integer NOT NULL,
    name character varying NOT NULL,
    description text
);


ALTER TABLE public.statuses OWNER TO admin;

--
-- Name: statuses_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.statuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.statuses_id_seq OWNER TO admin;

--
-- Name: statuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.statuses_id_seq OWNED BY public.statuses.id;


--
-- Name: suitcases; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.suitcases (
    id integer NOT NULL,
    test_case_id integer NOT NULL,
    test_suite_id integer NOT NULL
);


ALTER TABLE public.suitcases OWNER TO admin;

--
-- Name: suitcases_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.suitcases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suitcases_id_seq OWNER TO admin;

--
-- Name: suitcases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.suitcases_id_seq OWNED BY public.suitcases.id;


--
-- Name: test_case_versions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.test_case_versions (
    id integer NOT NULL,
    test_case_id integer NOT NULL,
    created_by integer NOT NULL,
    release_ready boolean,
    version integer NOT NULL,
    name character varying,
    description text,
    steps text,
    expected_result text,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.test_case_versions OWNER TO admin;

--
-- Name: test_case_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.test_case_versions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_case_versions_id_seq OWNER TO admin;

--
-- Name: test_case_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.test_case_versions_id_seq OWNED BY public.test_case_versions.id;


--
-- Name: test_cases; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.test_cases (
    id integer NOT NULL,
    scenario_id integer NOT NULL,
    status_set_id integer NOT NULL
);


ALTER TABLE public.test_cases OWNER TO admin;

--
-- Name: test_cases_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.test_cases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_cases_id_seq OWNER TO admin;

--
-- Name: test_cases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.test_cases_id_seq OWNED BY public.test_cases.id;


--
-- Name: test_suites; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.test_suites (
    id integer NOT NULL,
    name character varying
);


ALTER TABLE public.test_suites OWNER TO admin;

--
-- Name: test_suites_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.test_suites_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.test_suites_id_seq OWNER TO admin;

--
-- Name: test_suites_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.test_suites_id_seq OWNED BY public.test_suites.id;


--
-- Name: user_groups; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_groups (
    id integer NOT NULL,
    created_by_id integer NOT NULL,
    owner_id integer NOT NULL,
    name character varying
);


ALTER TABLE public.user_groups OWNER TO admin;

--
-- Name: user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.user_groups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_groups_id_seq OWNER TO admin;

--
-- Name: user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.user_groups_id_seq OWNED BY public.user_groups.id;


--
-- Name: user_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_types (
    id integer NOT NULL,
    name character varying NOT NULL,
    description text
);


ALTER TABLE public.user_types OWNER TO admin;

--
-- Name: user_types_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.user_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_types_id_seq OWNER TO admin;

--
-- Name: user_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.user_types_id_seq OWNED BY public.user_types.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    user_group_id integer,
    user_type_id integer NOT NULL,
    first_name character varying NOT NULL,
    last_name character varying NOT NULL,
    email character varying NOT NULL,
    password character varying NOT NULL,
    active boolean,
    created_at timestamp with time zone DEFAULT now(),
    last_login_at timestamp with time zone
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: attachments id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.attachments ALTER COLUMN id SET DEFAULT nextval('public.attachments_id_seq'::regclass);


--
-- Name: clients id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.clients ALTER COLUMN id SET DEFAULT nextval('public.clients_id_seq'::regclass);


--
-- Name: devices id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.devices ALTER COLUMN id SET DEFAULT nextval('public.devices_id_seq'::regclass);


--
-- Name: executions id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions ALTER COLUMN id SET DEFAULT nextval('public.executions_id_seq'::regclass);


--
-- Name: projects id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.projects ALTER COLUMN id SET DEFAULT nextval('public.projects_id_seq'::regclass);


--
-- Name: resolutions id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resolutions ALTER COLUMN id SET DEFAULT nextval('public.resolutions_id_seq'::regclass);


--
-- Name: runs id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.runs ALTER COLUMN id SET DEFAULT nextval('public.runs_id_seq'::regclass);


--
-- Name: scenarios id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scenarios ALTER COLUMN id SET DEFAULT nextval('public.scenarios_id_seq'::regclass);


--
-- Name: sessions id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sessions ALTER COLUMN id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: status_sets id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.status_sets ALTER COLUMN id SET DEFAULT nextval('public.status_sets_id_seq'::regclass);


--
-- Name: statuses id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.statuses ALTER COLUMN id SET DEFAULT nextval('public.statuses_id_seq'::regclass);


--
-- Name: suitcases id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.suitcases ALTER COLUMN id SET DEFAULT nextval('public.suitcases_id_seq'::regclass);


--
-- Name: test_case_versions id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_case_versions ALTER COLUMN id SET DEFAULT nextval('public.test_case_versions_id_seq'::regclass);


--
-- Name: test_cases id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_cases ALTER COLUMN id SET DEFAULT nextval('public.test_cases_id_seq'::regclass);


--
-- Name: test_suites id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_suites ALTER COLUMN id SET DEFAULT nextval('public.test_suites_id_seq'::regclass);


--
-- Name: user_groups id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_groups ALTER COLUMN id SET DEFAULT nextval('public.user_groups_id_seq'::regclass);


--
-- Name: user_types id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_types ALTER COLUMN id SET DEFAULT nextval('public.user_types_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attachments attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.attachments
    ADD CONSTRAINT attachments_pkey PRIMARY KEY (id);


--
-- Name: clients clients_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_name_key UNIQUE (name);


--
-- Name: clients clients_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (id);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- Name: executions executions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: resolutions resolutions_hw_unique; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resolutions
    ADD CONSTRAINT resolutions_hw_unique UNIQUE (h, w);


--
-- Name: resolutions resolutions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resolutions
    ADD CONSTRAINT resolutions_pkey PRIMARY KEY (id);


--
-- Name: runs runs_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_pkey PRIMARY KEY (id);


--
-- Name: scenarios scenarios_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_name_key UNIQUE (name);


--
-- Name: scenarios scenarios_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scenarios
    ADD CONSTRAINT scenarios_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_token_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_token_key UNIQUE (token);


--
-- Name: status_sets status_sets_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.status_sets
    ADD CONSTRAINT status_sets_name_key UNIQUE (name);


--
-- Name: status_sets status_sets_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.status_sets
    ADD CONSTRAINT status_sets_pkey PRIMARY KEY (id);


--
-- Name: statuses statuses_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.statuses
    ADD CONSTRAINT statuses_pkey PRIMARY KEY (id);


--
-- Name: suitcases suitcases_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.suitcases
    ADD CONSTRAINT suitcases_pkey PRIMARY KEY (id);


--
-- Name: suitcases suitcases_test_case_id_test_suite_id_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.suitcases
    ADD CONSTRAINT suitcases_test_case_id_test_suite_id_key UNIQUE (test_case_id, test_suite_id);


--
-- Name: test_case_versions test_case_version_unique; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_case_versions
    ADD CONSTRAINT test_case_version_unique UNIQUE (test_case_id, version);


--
-- Name: test_case_versions test_case_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_case_versions
    ADD CONSTRAINT test_case_versions_pkey PRIMARY KEY (id);


--
-- Name: test_cases test_cases_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_pkey PRIMARY KEY (id);


--
-- Name: test_suites test_suites_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_suites
    ADD CONSTRAINT test_suites_name_key UNIQUE (name);


--
-- Name: test_suites test_suites_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_suites
    ADD CONSTRAINT test_suites_pkey PRIMARY KEY (id);


--
-- Name: user_groups user_groups_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_name_key UNIQUE (name);


--
-- Name: user_groups user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_groups
    ADD CONSTRAINT user_groups_pkey PRIMARY KEY (id);


--
-- Name: user_types user_types_name_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_types
    ADD CONSTRAINT user_types_name_key UNIQUE (name);


--
-- Name: user_types user_types_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_types
    ADD CONSTRAINT user_types_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: attachment_edited_at_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX attachment_edited_at_idx ON public.attachments USING btree (edited_at);


--
-- Name: attachment_edited_by_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX attachment_edited_by_idx ON public.attachments USING btree (edited_by);


--
-- Name: attachment_filename_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX attachment_filename_idx ON public.attachments USING btree (filename);


--
-- Name: attachment_parent_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX attachment_parent_idx ON public.attachments USING btree (parent_attachment_id);


--
-- Name: attachment_uploaded_at_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX attachment_uploaded_at_idx ON public.attachments USING btree (uploaded_at);


--
-- Name: attachment_uploaded_by_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX attachment_uploaded_by_idx ON public.attachments USING btree (uploaded_by);


--
-- Name: device_project_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX device_project_idx ON public.devices USING btree (project_id);


--
-- Name: execution_attachment_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX execution_attachment_idx ON public.executions USING btree (attachment_id);


--
-- Name: execution_device_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX execution_device_idx ON public.executions USING btree (device_id);


--
-- Name: execution_executor_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX execution_executor_idx ON public.executions USING btree (executed_by);


--
-- Name: execution_run_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX execution_run_idx ON public.executions USING btree (run_id);


--
-- Name: execution_status_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX execution_status_idx ON public.executions USING btree (status_id);


--
-- Name: execution_test_case_version_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX execution_test_case_version_idx ON public.executions USING btree (test_case_version_id);


--
-- Name: project_name_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX project_name_idx ON public.projects USING btree (name);


--
-- Name: run_name_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX run_name_idx ON public.runs USING btree (name);


--
-- Name: run_project_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX run_project_idx ON public.runs USING btree (project_id);


--
-- Name: session_token_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX session_token_idx ON public.sessions USING btree (token);


--
-- Name: session_user_id_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX session_user_id_idx ON public.sessions USING btree (user_id);


--
-- Name: status_name_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX status_name_idx ON public.statuses USING btree (name);


--
-- Name: status_status_set_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX status_status_set_idx ON public.statuses USING btree (status_set_id);


--
-- Name: suitcase_test_case_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX suitcase_test_case_idx ON public.suitcases USING btree (test_case_id);


--
-- Name: suitcase_test_suite_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX suitcase_test_suite_idx ON public.suitcases USING btree (test_suite_id);


--
-- Name: test_case_scenario_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX test_case_scenario_idx ON public.test_cases USING btree (scenario_id);


--
-- Name: test_case_status_set_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX test_case_status_set_idx ON public.test_cases USING btree (status_set_id);


--
-- Name: test_case_version_created_at_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX test_case_version_created_at_idx ON public.test_case_versions USING btree (created_at);


--
-- Name: test_case_version_created_by_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX test_case_version_created_by_idx ON public.test_case_versions USING btree (created_by);


--
-- Name: test_case_version_test_case_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX test_case_version_test_case_idx ON public.test_case_versions USING btree (test_case_id);


--
-- Name: user_group_created_by_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX user_group_created_by_idx ON public.user_groups USING btree (created_by_id);


--
-- Name: user_group_owner_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX user_group_owner_idx ON public.user_groups USING btree (owner_id);


--
-- Name: user_user_group_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX user_user_group_idx ON public.users USING btree (user_group_id);


--
-- Name: user_user_type_idx; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX user_user_type_idx ON public.users USING btree (user_type_id);


--
-- Name: attachments attachments_edited_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.attachments
    ADD CONSTRAINT attachments_edited_by_fkey FOREIGN KEY (edited_by) REFERENCES public.users(id);


--
-- Name: attachments attachments_parent_attachment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.attachments
    ADD CONSTRAINT attachments_parent_attachment_id_fkey FOREIGN KEY (parent_attachment_id) REFERENCES public.attachments(id);


--
-- Name: attachments attachments_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.attachments
    ADD CONSTRAINT attachments_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id);


--
-- Name: devices devices_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.devices
    ADD CONSTRAINT devices_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: executions executions_attachment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_attachment_id_fkey FOREIGN KEY (attachment_id) REFERENCES public.attachments(id);


--
-- Name: executions executions_device_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_device_id_fkey FOREIGN KEY (device_id) REFERENCES public.devices(id);


--
-- Name: executions executions_executed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_executed_by_fkey FOREIGN KEY (executed_by) REFERENCES public.users(id);


--
-- Name: executions executions_resolution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_resolution_id_fkey FOREIGN KEY (resolution_id) REFERENCES public.resolutions(id);


--
-- Name: executions executions_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_run_id_fkey FOREIGN KEY (run_id) REFERENCES public.runs(id);


--
-- Name: executions executions_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.statuses(id);


--
-- Name: executions executions_test_case_version_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.executions
    ADD CONSTRAINT executions_test_case_version_id_fkey FOREIGN KEY (test_case_version_id) REFERENCES public.test_case_versions(id);


--
-- Name: projects projects_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(id);


--
-- Name: runs runs_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.runs
    ADD CONSTRAINT runs_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: statuses statuses_status_set_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.statuses
    ADD CONSTRAINT statuses_status_set_id_fkey FOREIGN KEY (status_set_id) REFERENCES public.status_sets(id);


--
-- Name: suitcases suitcases_test_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.suitcases
    ADD CONSTRAINT suitcases_test_case_id_fkey FOREIGN KEY (test_case_id) REFERENCES public.test_cases(id);


--
-- Name: suitcases suitcases_test_suite_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.suitcases
    ADD CONSTRAINT suitcases_test_suite_id_fkey FOREIGN KEY (test_suite_id) REFERENCES public.test_suites(id);


--
-- Name: test_case_versions test_case_versions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_case_versions
    ADD CONSTRAINT test_case_versions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: test_case_versions test_case_versions_test_case_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_case_versions
    ADD CONSTRAINT test_case_versions_test_case_id_fkey FOREIGN KEY (test_case_id) REFERENCES public.test_cases(id);


--
-- Name: test_cases test_cases_scenario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_scenario_id_fkey FOREIGN KEY (scenario_id) REFERENCES public.scenarios(id);


--
-- Name: test_cases test_cases_status_set_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.test_cases
    ADD CONSTRAINT test_cases_status_set_id_fkey FOREIGN KEY (status_set_id) REFERENCES public.status_sets(id);


--
-- Name: users users_user_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_user_type_id_fkey FOREIGN KEY (user_type_id) REFERENCES public.user_types(id);


--
-- PostgreSQL database dump complete
--


