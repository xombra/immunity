#include <Python.h>
#include <sched.h>
#include <sys/mount.h>
#include <linux/fs.h>
#include <sys/capability.h>
#include <sys/prctl.h>

#ifndef MNT_DETACH
#define MNT_DETACH      0x00000002
#endif

static PyObject *ImmunityException;

static PyObject* unshare_newns(PyObject *self, PyObject *args);

PyObject* unshare_newns(PyObject *self, PyObject *args)
{
  if (unshare(CLONE_NEWNS) < 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* do_mount_bind(PyObject *self, PyObject *args);

PyObject* do_mount_bind(PyObject *self, PyObject *args)
{
  const char *source, *target;
  if (!PyArg_ParseTuple(args, "ss", &source, &target)) {
    return NULL;
  }
  if (mount(source, target, NULL, MS_BIND, NULL) != 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* do_mount_tmpfs(PyObject *self, PyObject *args);

PyObject* do_mount_tmpfs(PyObject *self, PyObject *args)
{
  const char *dir;
  if (!PyArg_ParseTuple(args, "s", &dir)) {
    return NULL;
  }
  if (mount("tmpfs", dir, "tmpfs", MS_NOSUID, "mode=0755") != 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* do_mount_proc(PyObject *self, PyObject *args);

PyObject* do_mount_proc(PyObject *self, PyObject *args)
{
  if (mount("proc", "/mnt/proc", "proc", MS_RDONLY, 0) != 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* do_remount(PyObject *self, PyObject *args);

PyObject* do_remount(PyObject *self, PyObject *args)
{
  const char *dir;
  if (!PyArg_ParseTuple(args, "s", &dir)) {
    return NULL;
  }
  if (mount(NULL, dir, NULL, MS_REMOUNT | MS_NODEV | MS_NOSUID, NULL) != 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* do_umount(PyObject *self, PyObject *args);

PyObject* do_umount(PyObject *self, PyObject *args)
{
  const char *dir;
  if (!PyArg_ParseTuple(args, "s", &dir)) {
    return NULL;
  }
  if (umount2(dir, MNT_DETACH) != 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* do_set_cap(PyObject *self, PyObject *args);

PyObject* do_set_cap(PyObject *self, PyObject *args)
{
  const char *cap_text;
  cap_t caps;

  if (!PyArg_ParseTuple(args, "s", &cap_text)) {
    return NULL;
  }
  caps = cap_from_text(cap_text);
  if (!caps) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }
  if (cap_set_proc(caps) == -1) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }
  if (cap_free(caps)) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* keep_caps(PyObject *self, PyObject *args);

PyObject* keep_caps(PyObject *self, PyObject *args)
{
  if (prctl(PR_SET_KEEPCAPS, 1, 0, 0, 0) < 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject* lock_caps(PyObject *self, PyObject *args);

#define SECURE_NOROOT                   0
#define SECURE_NOROOT_LOCKED            1
#define SECURE_NO_SETUID_FIXUP          2
#define SECURE_NO_SETUID_FIXUP_LOCKED   3
#define SECURE_KEEP_CAPS                4
#define SECURE_KEEP_CAPS_LOCKED         5

PyObject* lock_caps(PyObject *self, PyObject *args)
{
  int cap;

  if (prctl(PR_SET_KEEPCAPS, 0, 0, 0, 0) < 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }
  if (prctl(PR_SET_SECUREBITS,
    1 << SECURE_KEEP_CAPS_LOCKED |
    1 << SECURE_NO_SETUID_FIXUP |
    1 << SECURE_NO_SETUID_FIXUP_LOCKED |
    1 << SECURE_NOROOT |
    1 << SECURE_NOROOT_LOCKED) < 0) {
    PyErr_SetFromErrno(ImmunityException);
    return NULL;
  }
  for(cap = 0; cap <= CAP_LAST_CAP; cap++) {
    if (prctl(PR_CAPBSET_DROP, cap, 0, 0, 0) < 0) {
      PyErr_SetFromErrno(ImmunityException);
      return NULL;
    }
  }

  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef ImmunityMethods[] = {
  {"unshare_newns",  unshare_newns, METH_VARARGS, "unshare(newns)"},
  {"mount_bind",  do_mount_bind, METH_VARARGS, "mount(,,,MS_BIND,)"},
  {"mount_tmpfs",  do_mount_tmpfs, METH_VARARGS, "mount(,,tmpfs,MS_NOSUID,mode=0755)"},
  {"mount_proc",  do_mount_proc, METH_VARARGS, "proc(,/proc,proc,MS_RDONLY,)"},
  {"remount",  do_remount, METH_VARARGS, "mount(,,,MS_REMOUNT|MS_NODEV|MS_NOSUID,)"},
  {"umount",  do_umount, METH_VARARGS, "umount2(,MNT_DETACH)"},
  {"set_cap",  do_set_cap, METH_VARARGS, "set_cap"},
  {"keep_caps",  keep_caps, METH_VARARGS, "keep_caps"},
  {"lock_caps",  lock_caps, METH_VARARGS, "lock_caps"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initimmunity(void)
{
  PyObject* module;
  module = Py_InitModule("immunity", ImmunityMethods);
  if (!module) {
    return;
  }
  ImmunityException = PyErr_NewException("immunity.error", NULL, NULL);
  PyModule_AddObject(module, "error", ImmunityException);
}

