#include <Python.h>
#include "procenet_api.h"


static PyObject *
posix_error(void)
{
  return PyErr_SetFromErrno(PyExc_OSError);
}


static PyObject *
py_invite(PyObject *self, PyObject *args)
{
  int status;
  int pid;
  char *message;

  if (!PyArg_ParseTuple(args, "iz", &pid, &message))
    return NULL;

  status = procenet_invite(pid, message);

  if (status < 0)
    return posix_error();

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *
py_respond(PyObject *self, PyObject *args)
{
  int pid;
  int status;
  int response;

  if (!PyArg_ParseTuple(args, "ii", &pid, &response))
    return NULL;

  status = procenet_respond(pid, response);
  
  if (status < 0) {
    return posix_error();
  }

  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *
py_invitations(PyObject *self, PyObject *args)
{
  int size;
  int res;
  int written, remaining;
  int i;
  struct invitation_t *invitations;
  PyObject* py_invitations;
  PyObject* ret;

  if (!PyArg_ParseTuple(args, "i", &size))
    return NULL;

  invitations = malloc(sizeof(struct invitation_t)*size);
  if (!invitations && size != 0)
      return PyErr_NoMemory();

  res = procenet_invitations(invitations, size);

  if (res < 0) {
    free(invitations);
    return posix_error();
  }
  remaining = res;

  for (written=0; written < size; written++) {
      if (invitations[written].pid == 0) break;
  }
  py_invitations = PyTuple_New(written);
  if (!py_invitations) {
      free(invitations);
      return NULL;
  }

  for (i=0; i<written; i++) {
      if (PyTuple_SetItem(py_invitations, i, Py_BuildValue("is", invitations[i].pid, invitations[i].message)) != 0) {
          free(invitations);
          return NULL;
      }
  }
  free(invitations);

  ret = PyTuple_New(2);
  if (!ret) return NULL;
  if ((PyTuple_SetItem(ret, 0, py_invitations) != 0) ||
          (PyTuple_SetItem(ret, 1, Py_BuildValue("i", remaining)) != 0)) {
      return NULL;
  }
  return ret;
}

static PyObject *
py_info(PyObject *self, PyObject *args)
{
  int pid;
  int i, count;
  struct friend_t friends_list[MAX_FRIENDS];
  PyObject* py_friends;

  if (!PyArg_ParseTuple(args, "i", &pid))
    return NULL;

  count = procenet_info(pid, friends_list);
  
  if (count < 0) {
    return posix_error();
  }

  py_friends = PyTuple_New(count);
  if (!py_friends) {
      return NULL;
  }

  for (i=0; i<count; i++) {
      if (PyTuple_SetItem(py_friends, i, Py_BuildValue("ii", friends_list[i].pid, friends_list[i].alive)) != 0) {
          return NULL;
      }
  }
  return py_friends;
}


static PyMethodDef msgMethods[] = {
  {"invite",  py_invite, METH_VARARGS,
   "Invite a process to be friends.\nExample:\ninvite(123, None) # Use default message\ninvite(123, \"Hello!\") # Use custom message"},
  {"respond",  py_respond, METH_VARARGS,
   "Respond to a friend request.\nExample:\nrespond(123, 1) # Accept"},
  {"invitations",  py_invitations, METH_VARARGS,
   "Get pending friend invitations and remaining invitations.\nExample:\n(invitations, remaining) = invitations(3)\nprint len(invitations), \"received. First one is from:\", invitations[0][0], \"with message:\", invitations[0][1]"},
  {"info",  py_info, METH_VARARGS,
   "Get friends list for the given process.\nExample:\nfriends = info(12)\nprint len(friends), \"total friends\""},
  {NULL, NULL, 0, NULL} 
};


void
initpyProcenet(void)
{
  (void) Py_InitModule("pyProcenet", msgMethods);
}
