import { React, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import axios from 'axios';
import './app.scss';

function App() {

	const [projects, setProjects] = useState([]);
	const [showNewProject, setShowNewProject] = useState(false);
	const [formData, setFormData] = useState({
		id: '',
		title: '',
		pid: '',
		group: '',
		description: ''
	});
	const jwt = document.cookie.split('; ').find((row) => row.startsWith('JWT='))?.split('=')[1];
	const egojwt = document.cookie.split('; ').find((row) => row.startsWith('EGOJWT='))?.split('=')[1];
	const [user, setUser] = useState({});
	const [groups, setGroups] = useState([]);

	useEffect(() => {

		getProjects();
		getGreeting();
		getGroups();




	}, [])

	useEffect(() => {

	}, [projects]);

	const getProjects = () => {
		axios.get('http://localhost:5000/api/projects/',{
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${jwt}`
		}})
			.then(response => setProjects(response.data))
			.catch(error => console.error(error));
	}

	const handleChange = (e) => {
		setFormData({ ...formData, [e.target.name]: e.target.value });
	};

	const handleSubmit = (e) => {
		e.preventDefault();

		if (formData.id !== '') {
			console.log(formData);
			axios.put(`http://localhost:5000/api/projects/`, formData,{
				headers: {
					'Content-Type': 'application/json',
					'Authorization': `Bearer ${jwt}`
			}})
				.then(response => {
					console.log(response);
					getProjects();
					document.getElementById('new_project').close();
				})
				.catch(error => console.error(error));
			return;
		}
		axios.post('http://localhost:5000/api/projects/', formData,{
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${jwt}`
		}})
			.then(response => {
				getProjects();
				document.getElementById('new_project').close();
			})
			.catch(error => console.error(error));

	};

	const newProject = () => {
		
		setFormData({
			id: '',
			title: '',
			pid: '',
			group: '',
			description: ''
		});
		
		document.getElementById('new_project').showModal()

	}

	const editProject = (project) => {

		setFormData(project);

		document.getElementById('new_project').showModal();

	}

	const deleteProject = (id) => {

		

		axios.delete('http://localhost:5000/api/projects/', { data: { id: id } },{
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${jwt}`
		}})
			.then(response => {
				getProjects();
				document.getElementById('new_project').close();
			})
			.catch(error => console.error(error));
	}

	const getGroups = () => {
		axios.get('https://apaego.sanbi.ac.za/api/groups', {
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${egojwt}`
		}}).then(response => {
			setGroups(response.data.resultSet);
		});
	}

	const getGreeting = () => {
		axios.get('http://localhost:5000/api/', {
			headers: {
				'Content-Type': 'application/json',
				'Authorization': `Bearer ${jwt}`
		}}).then(response => {
			setUser(response.data);
		});
	}

	const updateToken = () => {
		axios.get('http://localhost:5000/api/generate-token').then(response => {
			document.cookie = `JWT=${response.data.token}`;
			window.location.reload();
		});
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
				<button className="btn btn-primary btn-sm ms-2" onClick={() => document.getElementById('user').showModal()}>USER</button>
				<button className="btn btn-primary btn-sm ms-2" onClick={() => updateToken()}>UPDATE TOKEN</button>
			</p>


			<table className="table">
				<thead>
					<tr>
						<th>ID</th>
						<th>PID</th>
						<th>Group</th>
						<th>Title</th>
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
							<td>{project.pid}</td>
							<td>{project.group}</td>
							<td>{project.title}</td>
							<td>{project.description}</td>
							<td>{project.owner_id}</td>
							<td>{project.created_at}</td>
							<td>{project.updated_at}</td>
							<td>
								<button className="btn btn-sm btn-light" onClick={() => editProject(project)}>Edit</button>
							</td>
						</tr>
					))}
				</tbody>
			</table>

			
			
			

			<dialog id="new_project" className="modal">
				<div className="modal-box">
					<h3 className="font-bold text-lg">{ formData.id !== '' ? 'Edit Project' : 'Add a new Project'}</h3>
					<form onSubmit={handleSubmit}>
						<input type="hidden" name="id" value={formData.id !== undefined ? formData.id : ''} />
						<p className="py-4">
							<input
								type="text"
								placeholder="Project Title"
								className="input input-bordered w-full"
								name="title"
								value={formData.title}
								onChange={handleChange}
							/>
						</p>
						<p className="py-4">
							<input
								type="text"
								placeholder="Project ID"
								className="input input-bordered w-full"
								name="pid"
								value={formData.pid}
								onChange={handleChange}
							/>
						</p>
						<p className="py-4">
							<select className="select select-bordered w-full" onChange={handleChange} name="group" value={formData.group} name="group">
								<option disabled selected>Select a Group</option>
								{
									groups.map(group => (
										<option key={group.name} value={group.name}>{group.name}</option>
									))
								}
							</select>
						</p>
						<p className="py-4">
							<textarea
								className="textarea textarea-bordered w-full"
								placeholder="Project Description"
								name="description"
								value={formData.description}
								onChange={handleChange}
							/>
						</p>
						<p className="py-4">
							<button className="btn btn-primary" type="submit">
								{
									formData.id !== '' ? 'UPDATE' : 'ADD'
								}
							</button>
							{ formData.id !== '' && <button className="btn btn-accent ms-2" onClick={() => deleteProject(formData.id)}>DELETE</button> }

						</p>

					</form>
				</div>
				<form method="dialog" className="modal-backdrop">
					<button>close</button>
				</form>
			</dialog>

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





		</div>
	);
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);