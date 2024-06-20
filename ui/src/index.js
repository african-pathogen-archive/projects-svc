import { React, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';
import './app.scss';

function App() {

	const [projects, setProjects] = useState([]);
	const [pathogens, setPathogens] = useState([]);
	const [projectFormData, setProjectFormData] = useState({
		id: '',
		title: '',
		pid: '',
		pathogen_id: '',
		group: '',
		description: ''
	});
	const [pathogenFormData, setPathogenFormData] = useState({
		id: '',
		common_name: '',
		scientific_name: '',
		schema: ''
	});
	const [user, setUser] = useState({});
	const [groups, setGroups] = useState([]);
	const [schemas, setSchemas] = useState([]);

	const jwt = document.cookie.split('; ').find((row) => row.startsWith('JWT='))?.split('=')[1];
	const api = 'http://localhost:5000/api';
	const ego_api = 'https://apaego.sanbi.ac.za/api';
	const song_api = 'https://apasong.sanbi.ac.za';
	const headers = {
		'Content-Type': 'application/json',
		'Authorization': `Bearer ${jwt}`
	};

	useEffect(() => {
		getProjects();
		getGreeting();
		getGroups();
		getPathogens();
		getSchemas();
	}, []);

	// GENERAL

	const getGreeting = () => {
		axios.get(api + '/', { headers: headers })
			.then(response => {
				setUser(response.data);
			})
			.catch(error => console.error(error));
	}

	// PROJECTS

	const getProjects = () => {
		axios.get(api + '/projects/', { headers: headers })
			.then(response => setProjects(response.data))
			.catch(error => console.error(error));
	}

	const handleProjectChange = (e) => {
		setProjectFormData({ ...projectFormData, [e.target.name]: e.target.value });
	};

	const handleProjectSubmit = (e) => {
		e.preventDefault();
			
		if (projectFormData.id !== '') {
			axios.put(api + '/projects/', projectFormData, { headers: headers })
				.then(response => {
					getProjects();
					document.getElementById('project').close();
				})
				.catch(error => console.error(error));
			return;
		}
		axios.post(api + '/projects/', projectFormData, { headers: headers })
			.then(response => {
				getProjects();
				document.getElementById('project').close();
			})
			.catch(error => console.error(error));
	};

	const newProject = () => {

		setProjectFormData({
			id: '',
			title: '',
			pid: '',
			pathogen_id: '',
			group: '',
			description: ''
		});

		document.getElementById('project').showModal()

	}
	
	const editProject = (project) => {
		setFormData(project);
		document.getElementById('project').showModal();
	}

	const deleteProject = (id) => {
		axios.delete(api + '/projects/', { data: { id: id }, headers: headers })
			.then(response => {
				getProjects();
				document.getElementById('project').close();
			})
			.catch(error => console.error(error));
	}

	// PATHOGENS

	const getPathogens = () => {
		axios.get(api + '/pathogens/', { headers: headers })
			.then(response => setPathogens(response.data))
			.catch(error => console.error(error));
	}

	const handlePathogenChange = (e) => {
		setPathogenFormData({ ...pathogenFormData, [e.target.name]: e.target.value });
	};

	const handlePathogenSubmit = (e) => {
		e.preventDefault();
		
		if (pathogenFormData.id !== '') {
			axios.put(api + '/pathogens/', pathogenFormData, { headers: headers })
				.then(response => {
					getPathogens();
					document.getElementById('pathogen').close();
				})
				.catch(error => console.error(error));
			return;
		}
		axios.post(api + '/pathogens/', pathogenFormData, { headers: headers })
			.then(response => {
				getPathogens();
				document.getElementById('pathogen').close();
			})
			.catch(error => console.error(error));

	};

	const newPathogen = () => {
		setPathogenFormData({
			id: '',
			common_name: '',
			scientific_name: '',
			schema: ''
		});
		document.getElementById('pathogen').showModal();
	}


	const editPathogen = (pathogen) => {
		setPathogenFormData(pathogen);
		document.getElementById('pathogen').showModal();
	}

	const deletePathogen = (id) => {
		axios.delete(api + '/pathogens/', { data: { id: id }, headers: headers })
			.then(response => {
				getPathogens();
				document.getElementById('pathogen').close();
			})
			.catch(error => console.error(error));
	}

	const getPathogenName = (id) => {
		console.log(id);
		const pathogen = pathogens.find(pathogen => pathogen.id === id);
		return pathogen ? pathogen.scientific_name : '';
	}

	// EGO API

	const getGroups = () => {
		axios.get(ego_api + '/groups', { headers: headers })
			.then(response => {
				setGroups(response.data.resultSet);
			})
			.catch(error => console.error(error));
	}
	

	const getGroupName = (id) => {
		const group = groups.find(group => group.id === id);
		return group ? group.name : '';
	}


	const UserName = ({ id }) => {
		const [userName, setUserName] = useState('');

		useEffect(() => {
			const getUserName = async (id) => {
				try {
					const response = await axios.get(`${ego_api}/users/${id}`, { headers: headers });
					setUserName(response.data.firstName + ' ' + response.data.lastName);
				} catch (error) {
					console.error(error);
				}
			};

			getUserName(id);
		}, [id]);

		return (
			<div>
				{userName}
			</div>
		);
	};

	// SONG API

	// This is using a project-service proxy, but should be changed to use the SONG API directly

	const getSchemas = () => {
		axios.get(api + '/schemas/', { headers: headers })
			.then(response => {
				console.log(response.data.resultSet); 
				setSchemas(response.data.resultSet)
			})
			.catch(error => console.error(error));
	}

	



	return (
		<div className="container mx-auto py-6">

			<div className="prose">
				<h1>Project Service</h1>
			</div>


			{
				user.message
			}


			<p className="py-4">
				<button className="btn btn-primary btn-sm" onClick={() => newProject()}>NEW PROJECT</button>
				<button className="btn btn-primary btn-sm ms-2" onClick={() => newPathogen()}>NEW PATHOGEN</button>
				<button className="btn btn-primary btn-sm ms-2" onClick={() => document.getElementById('user').showModal()}>USER</button>
			</p>

			<div className="prose my-5">
				<h3>Projects</h3>
			</div>

			<table className="table">
				<thead>
					<tr>
						<th>ID</th>
						<th>Title</th>
						<th>PID</th>
						<th>Pathogen</th>
						<th>Group</th>
						<th>Description</th>
						<th>Owner</th>
						<th>Created At</th>
						<th>Updated At</th>
						<th>Edit</th>
					</tr>
				</thead>
				<tbody>
					{projects.map(project => (
						<tr key={project.id}>
							<td>{project.id}</td>
							<td><span className="font-bold">{project.title}</span></td>
							<td>{project.pid}</td>
							<td>{getPathogenName(project.pathogen_id)}</td>
							<td>{getGroupName(project.group)}</td>
							<td>{project.description}</td>
							<td><UserName id={project.owner_id}/></td>
							<td>{project.created_at}</td>
							<td>{project.updated_at}</td>
							<td>
								<button className="btn btn-sm btn-light" onClick={() => editProject(project)}>Edit</button>
							</td>
						</tr>
					))}
				</tbody>
			</table>

			
			<div className="prose my-5">
				<h3>Pathogens</h3>
			</div>

			<table className="table">
				<thead>
					<tr>
						<th>ID</th>
						<th>Common Name</th>
						<th>Scientific Name</th>
						<th>Schema</th>
						<th>Edit</th>
					</tr>
				</thead>
				<tbody>
					{pathogens.map(pathogen => (
						<tr key={pathogen.id}>
							<td>{pathogen.id}</td>
							<td><span className="font-bold">{pathogen.common_name}</span></td>
							<td>{pathogen.scientific_name}</td>
							<td>{pathogen.schema}</td>
							<td>
								<button className="btn btn-sm btn-light" onClick={() => editPathogen(pathogen)}>Edit</button>
							</td>
						</tr>
					))}
				</tbody>
			</table>



			{/**** PROJECT ****/}
			<dialog id="project" className="modal">
				<div className="modal-box">
					<h3 className="font-bold text-lg">{projectFormData.id !== '' ? 'Edit Project' : 'Add a new Project'}</h3>
					<form onSubmit={handleProjectSubmit}>
						<input type="hidden" name="form" value='project' />
						<input type="hidden" name="id" value={projectFormData.id !== undefined ? projectFormData.id : ''} />
						<p className="py-4">
							<input
								type="text"
								placeholder="Project Title"
								className="input input-bordered w-full"
								name="title"
								value={projectFormData.title}
								onChange={handleProjectChange}
							/>
						</p>
						<p className="py-4">
							<input
								type="text"
								placeholder="Project ID"
								className="input input-bordered w-full"
								name="pid"
								value={projectFormData.pid}
								onChange={handleProjectChange}
							/>
						</p>
						<p className="py-4">
							<select className="select select-bordered w-full" onChange={handleProjectChange} name="pathogen_id" value={projectFormData.pathogen_id}>
								<option selected>Select a Pathogen</option>
								{
									pathogens.map(pathogen => (
										<option key={pathogen.id} value={pathogen.id}>{pathogen.scientific_name}</option>
									))
								}
							</select>
						</p>
						<p className="py-4">
							<select className="select select-bordered w-full" onChange={handleProjectChange} name="group" value={projectFormData.group}>
								<option disabled selected>Select a Group</option>
								{
									groups.map(group => (
										<option key={group.id} value={group.id}>{group.name}</option>
									))
								}
							</select>
						</p>
						<p className="py-4">
							<textarea
								className="textarea textarea-bordered w-full"
								placeholder="Project Description"
								name="description"
								value={projectFormData.description}
								onChange={handleProjectChange}
							/>
						</p>
						<p className="py-4">
							<button className="btn btn-primary" type="submit">
								{
									projectFormData.id !== '' ? 'UPDATE' : 'ADD'
								}
							</button>
							{projectFormData.id !== '' && <button className="btn btn-accent ms-2" onClick={() => deleteProject(projectFormData.id)}>DELETE</button>}

						</p>

					</form>
				</div>
				<form method="dialog" className="modal-backdrop">
					<button>close</button>
				</form>
			</dialog>

			{/**** USER ****/}
			<dialog id="user" className="modal">
				<div className="modal-box">
					<pre>
						{JSON.stringify(user, null, 2)}
					</pre>
				</div>
				<form method="dialog" className="modal-backdrop">
					<button>close</button>
				</form>
			</dialog>

			{/**** PATHOGEN ****/}
			<dialog id="pathogen" className="modal">
				<div className="modal-box">
					<h3 className="font-bold text-lg">{pathogenFormData.id !== '' ? 'Edit Pathogen' : 'Add a new Pathogen'}</h3>
					<form onSubmit={handlePathogenSubmit}>
						<input type="hidden" name="form" value='pathogen' />
						<input type="hidden" name="id" value={pathogenFormData.id !== undefined ? pathogenFormData.id : ''} />
						<p className="py-4">
							<input
								type="text"
								placeholder="Common Name"
								className="input input-bordered w-full"
								name="common_name"
								value={pathogenFormData.common_name}
								onChange={handlePathogenChange}
							/>
						</p>
						<p className="py-4">
							<input
								type="text"
								placeholder="Scientific Name"
								className="input input-bordered w-full"
								name="scientific_name"
								value={pathogenFormData.scientific_name}
								onChange={handlePathogenChange}
							/>
						</p>
						
						<p className="py-4">
							<select className="select select-bordered w-full" onChange={handleProjectChange} name="schema" value={projectFormData.schema}>
								<option selected>Select a Schema</option>
								{
									schemas.map((schema,index) => (
										<option key={index} value={`${schema.name}-${schema.version}`}>{schema.name} - {schema.version}</option>
									))
								}
							</select>
						</p>
						<p className="py-4">
							<button className="btn btn-primary" type="submit">
								{
									pathogenFormData.id !== '' ? 'UPDATE' : 'ADD'
								}
							</button>
							{pathogenFormData.id !== '' && <button className="btn btn-accent ms-2" onClick={() => deletePathogen(pathogenFormData.id)}>DELETE</button>}

						</p>

					</form>
				</div>
				<form method="dialog" className="modal-backdrop">
					<button>close</button>
				</form>
			</dialog>







		</div>
	);
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);