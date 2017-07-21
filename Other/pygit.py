# coding=utf-8
import argparse, collections, difflib, enum, hashlib, operator, os, stat
import struct, sys, time, urllib.request, zlib

# git索引中的一个条目的数据(. git /索引)
IndexEntry = collections.namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode', 'uid',
    'gid', 'size', 'sha1', 'flags', 'path',
])

class ObjectType(enum.Enum):
    """对象类型的枚举。还有其他类型的，但是我们不需要它们。
    在git的源代码中看到“enum object_type”(git / cache.h)。
    """
    commit = 1
    tree = 2
    blob = 3

def read_file(path):
    """在给定路径上读取文件的内容作为字节。"""
    with open(path,'rb') as f:
        return f.read()

def write_file(path,data):
    """在给定的路径上写入数据字节"""
    with open(path,'wb') as f:
        f.write(data)

def init(repo):
    """创建仓库目录，初始化.git目录"""
    os.mkdir(repo)
    os.mkdir(os.path.join(repo,'.git'))
    for name in ['object','refs','refs/heads']:
        os.mkdir(os.path.join(repo,'.git','HEAD'))
    write_file(os.path.join(repo,'.git','HEAD'),b'ref:refs/heads/master')
    print('initialized empty repository:{}'.format(repo))

def hash_object(data,obj_type,write=True):
    """根据对象类型计算对象的散列值，如果write是真的话，则保存到文件中。
    以十六进制字符串的形式返回SHA-1散列
    """
    header = '{} {}'.format(obj_type,len(data)).encode()
    full_data = header + b'\x00' + data
    sha1 = hashlib.sha1(full_data).hexdigest()
    if write:
        path = os.path.join('.git','objects',sha1[:2],sha1[2:])
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path),exist_ok=True)
            write_file(path,zlib.compress(full_data))
    return sha1

def find_object(sha1_prefix):
    """在对象存储中找到给定的sha - 1前缀和返回路径到对象的对象，
    或者在没有对象或多个对象的前缀时提高ValueError。
    """
    if len(sha1_prefix) < 2:
        raise ValueError('散列前缀必须是两个或多个字符')
    obj_dir = os.path.join('.git','objects',sha1_prefix[:2])
    rest = sha1_prefix[2:]
    objects = [name for name in os.listdir(obj_dir) if name.startswith(rest)]
    if not objects:
        raise ValueError('object {!r} not found'.format(sha1_prefix))
    if len(objects)>=2:
        raise ValueError('multiple objects({}) with prefix{!r}'.format(
            len(objects),sha1_prefix))
    return os.path.join(obj_dir,objects[0])

def read_object(sha1_prefix):
    """Read object with given SHA-1 prefix and return tuple of
    (object_type, data_bytes), or raise ValueError if not found.
    """
    path = find_object(sha1_prefix)
    full_data = zlib.decompress(read_object(path))
    nul_index = full_data.index(b'\x00')
    header = full_data[:nul_index]
    obj_type,size_str = header.decode().split()
    size = int(size_str)
    data = full_data[nul_index + 1:]
    assert size == len(data),'expected size {},got {} bytes'.format(
        size,len(data))
    return (obj_type,data)

def cat_file(mode,sha1_prefix):
    """将给定的sha - 1前缀写入到stdout中。
    如果模式是“commit”，“tree”或“blob”，打印原始数据字节的对象。
    如果模式是“大小”，打印对象的大小。如果模式是' type '，打印对象的类型。
    如果模式是“漂亮的”，打印一个漂亮的对象的版本。
    """
    obj_type,data = read_object(sha1_prefix)
    if mode in ['commit','tree','blob']:
        if obj_type != mode:
            raise ValueError('expected object type {},got{}'.format(
                mode,obj_type))
        sys.stdout.buffer.write(data)
    elif mode == 'size':
        print(len(data))
    elif mode == 'type':
        print(obj_type)
    elif mode == 'pretty':
        if obj_type in ['commit','blob']:
            sys.stdout.buffer.write(data)
        elif obj_type == 'tree':
            for mode,path,sha1 in read_object(data=data):
                type_str = 'tree' if stat.S_ISDIR(mode) else 'blob'
                print('{:06o} {} {}\t{}'.format(mode,type_str,sha1,path))
        else:
            assert False,'unhandled object type {!r}'.format(obj_type)
    else:
        raise ValueError('unexpected mode {!r}'.format(mode))

def read_index():
    """阅读git索引文件和索引条目对象的返回列表。"""
    try:
        data = read_file(os.path.join('.git', 'index'))
    except FileNotFoundError:
        return []
    digest = hashlib.sha1(data[:-20]).digest()
    assert digest == data[-20:], 'invalid index checksum'
    signature, version, num_entries = struct.unpack('!4sLL', data[:12])
    assert signature == b'DIRC', \
        'invalid index signature {}'.format(signature)
    assert version == 2, 'unknown index version {}'.format(version)
    entry_data = data[12:-20]
    entries = []
    i = 0
    while i + 62 < len(entry_data):
        fields_end = i + 62
        fields = struct.unpack('!LLLLLLLLLL20sH', entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields + (path.decode(),)))
        entries.append(entry)
        entry_len = ((62 + len(path) + 8) // 8) * 8
        i += entry_len
    assert len(entries) == num_entries
    return entries


def ls_files(details=False):
    """索引中的文件列表(包括模式、sha - 1和阶段号，如果“细节”是正确的)。
    """
    for entry in read_index():
        if details:
            stage = (entry.flags >> 12) & 3
            print('{:6o} {} {:}\t{}'.format(
                entry.mode, entry.sha1.hex(), stage, entry.path))
        else:
            print(entry.path)


def get_status():
    """获得工作副本的状态，返回tuple(changed_paths，new_paths，deleted_paths)。
    """
    paths = set()
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d != '.git']
        for file in files:
            path = os.path.join(root, file)
            path = path.replace('\\', '/')
            if path.startswith('./'):
                path = path[2:]
            paths.add(path)
    entries_by_path = {e.path: e for e in read_index()}
    entry_paths = set(entries_by_path)
    changed = {p for p in (paths & entry_paths)
               if hash_object(read_file(p), 'blob', write=False) !=
               entries_by_path[p].sha1.hex()}
    new = paths - entry_paths
    deleted = entry_paths - paths
    return (sorted(changed), sorted(new), sorted(deleted))


def status():
    """显示工作副本的状态。"""
    changed, new, deleted = get_status()
    if changed:
        print('changed files:')
        for path in changed:
            print('   ', path)
    if new:
        print('new files:')
        for path in new:
            print('   ', path)
    if deleted:
        print('deleted files:')
        for path in deleted:
            print('   ', path)


def diff():
    """显示更改的文件(在索引和工作副本之间)。"""
    changed, _, _ = get_status()
    entries_by_path = {e.path: e for e in read_index()}
    for i, path in enumerate(changed):
        sha1 = entries_by_path[path].sha1.hex()
        obj_type, data = read_object(sha1)
        assert obj_type == 'blob'
        index_lines = data.decode().splitlines()
        working_lines = read_file(path).decode().splitlines()
        diff_lines = difflib.unified_diff(
            index_lines, working_lines,
            '{} (index)'.format(path),
            '{} (working copy)'.format(path),
            lineterm='')
        for line in diff_lines:
            print(line)
        if i < len(changed) - 1:
            print('-' * 70)


def write_index(entries):
    """将索引条目对象的列表写到git索引文件中。"""
    packed_entries = []
    for entry in entries:
        entry_head = struct.pack('!LLLLLLLLLL20sH',
                                 entry.ctime_s, entry.ctime_n, entry.mtime_s, entry.mtime_n,
                                 entry.dev, entry.ino, entry.mode, entry.uid, entry.gid,
                                 entry.size, entry.sha1, entry.flags)
        path = entry.path.encode()
        length = ((62 + len(path) + 8) // 8) * 8
        packed_entry = entry_head + path + b'\x00' * (length - 62 - len(path))
        packed_entries.append(packed_entry)
    header = struct.pack('!4sLL', b'DIRC', 2, len(entries))
    all_data = header + b''.join(packed_entries)
    digest = hashlib.sha1(all_data).digest()
    write_file(os.path.join('.git', 'index'), all_data + digest)


def add(paths):
    """将所有文件路径添加到git索引。"""
    paths = [p.replace('\\', '/') for p in paths]
    all_entries = read_index()
    entries = [e for e in all_entries if e.path not in paths]
    for path in paths:
        sha1 = hash_object(read_file(path), 'blob')
        st = os.stat(path)
        flags = len(path.encode())
        assert flags < (1 << 12)
        entry = IndexEntry(
            int(st.st_ctime), 0, int(st.st_mtime), 0, st.st_dev,
            st.st_ino, st.st_mode, st.st_uid, st.st_gid, st.st_size,
            bytes.fromhex(sha1), flags, path)
        entries.append(entry)
    entries.sort(key=operator.attrgetter('path'))
    write_index(entries)


def write_tree():
    """从当前索引条目中写入树对象。"""
    tree_entries = []
    for entry in read_index():
        assert '/' not in entry.path, \
            'currently only supports a single, top-level directory'
        mode_path = '{:o} {}'.format(entry.mode, entry.path).encode()
        tree_entry = mode_path + b'\x00' + entry.sha1
        tree_entries.append(tree_entry)
    return hash_object(b''.join(tree_entries), 'tree')


def get_local_master_hash():
    """获取本地主分支的当前提交哈希(sha - 1字符串)。"""
    master_path = os.path.join('.git', 'refs', 'heads', 'master')
    try:
        return read_file(master_path).decode().strip()
    except FileNotFoundError:
        return None


def commit(message, author=None):
    """使用给定的消息提交索引的当前状态。提交对象的返回散列。
    """
    tree = write_tree()
    parent = get_local_master_hash()
    if author is None:
        author = '{} <{}>'.format(
            os.environ['GIT_AUTHOR_NAME'], os.environ['GIT_AUTHOR_EMAIL'])
    timestamp = int(time.mktime(time.localtime()))
    utc_offset = -time.timezone
    author_time = '{} {}{:02}{:02}'.format(
        timestamp,
        '+' if utc_offset > 0 else '-',
        abs(utc_offset) // 3600,
        (abs(utc_offset) // 60) % 60)
    lines = ['tree ' + tree]
    if parent:
        lines.append('parent ' + parent)
    lines.append('author {} {}'.format(author, author_time))
    lines.append('committer {} {}'.format(author, author_time))
    lines.append('')
    lines.append(message)
    lines.append('')
    data = '\n'.join(lines).encode()
    sha1 = hash_object(data, 'commit')
    master_path = os.path.join('.git', 'refs', 'heads', 'master')
    write_file(master_path, (sha1 + '\n').encode())
    print('committed to master: {:7}'.format(sha1))
    return sha1


def extract_lines(data):
    """从给定的服务器数据提取行列表。"""
    lines = []
    i = 0
    for _ in range(1000):
        line_length = int(data[i:i + 4], 16)
        line = data[i + 4:i + line_length]
        lines.append(line)
        if line_length == 0:
            i += 4
        else:
            i += line_length
        if i >= len(data):
            break
    return lines


def build_lines_data(lines):
    """从给定的线路构建字节字符串到服务器。"""
    result = []
    for line in lines:
        result.append('{:04x}'.format(len(line) + 5).encode())
        result.append(line)
        result.append(b'\n')
    result.append(b'0000')
    return b''.join(result)


def http_request(url, username, password, data=None):
    """对给定的URL进行一个经过验证的HTTP请求(默认情况下，如果“数据”不是没有的话)。
    """
    password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_manager.add_password(None, url, username, password)
    auth_handler = urllib.request.HTTPBasicAuthHandler(password_manager)
    opener = urllib.request.build_opener(auth_handler)
    f = opener.open(url, data=data)
    return f.read()


def get_remote_master_hash(git_url, username, password):
    """获取远程主分支的提交哈希，返回sha - 1十六进制字符串或没有远程提交。
    """
    url = git_url + '/info/refs?service=git-receive-pack'
    response = http_request(url, username, password)
    lines = extract_lines(response)
    assert lines[0] == b'# service=git-receive-pack\n'
    assert lines[1] == b''
    if lines[2][:40] == b'0' * 40:
        return None
    master_sha1, master_ref = lines[2].split(b'\x00')[0].split()
    assert master_ref == b'refs/heads/master'
    assert len(master_sha1) == 40
    return master_sha1.decode()


def read_tree(sha1=None, data=None):
    """使用给定的sha - 1(十六进制字符串)或数据读取树对象，并返回(模式、路径、sha1)元组的列表。
    """
    if sha1 is not None:
        obj_type, data = read_object(sha1)
        assert obj_type == 'tree'
    elif data is None:
        raise TypeError('must specify "sha1" or "data"')
    i = 0
    entries = []
    for _ in range(1000):
        end = data.find(b'\x00', i)
        if end == -1:
            break
        mode_str, path = data[i:end].decode().split()
        mode = int(mode_str, 8)
        digest = data[end + 1:end + 21]
        entries.append((mode, path, digest.hex()))
        i = end + 1 + 20
    return entries


def find_tree_objects(tree_sha1):
    """返回树中的所有对象的sha - 1散列(递归地)，包括树本身的散列。
    """
    objects = {tree_sha1}
    for mode, path, sha1 in read_tree(sha1=tree_sha1):
        if stat.S_ISDIR(mode):
            objects.update(find_tree_objects(sha1))
        else:
            objects.add(sha1)
    return objects


def find_commit_objects(commit_sha1):
    """返回集合中的所有对象的sha - 1散列(递归地)、它的树、它的父类以及提交本身的散列。
    """
    objects = {commit_sha1}
    obj_type, commit = read_object(commit_sha1)
    assert obj_type == 'commit'
    lines = commit.decode().splitlines()
    tree = next(l[5:45] for l in lines if l.startswith('tree '))
    objects.update(find_tree_objects(tree))
    parents = (l[7:47] for l in lines if l.startswith('parent '))
    for parent in parents:
        objects.update(find_commit_objects(parent))
    return objects


def find_missing_objects(local_sha1, remote_sha1):
    """返回在远程(基于给定的远程提交散列)的本地提交中丢失的对象的sha - 1散列。
    """
    local_objects = find_commit_objects(local_sha1)
    if remote_sha1 is None:
        return local_objects
    remote_objects = find_commit_objects(remote_sha1)
    return local_objects - remote_objects


def encode_pack_object(obj):
    """为包文件和返回字节(后面是压缩的数据字节)编码单个对象。
    """
    obj_type, data = read_object(obj)
    type_num = ObjectType[obj_type].value
    size = len(data)
    byte = (type_num << 4) | (size & 0x0f)
    size >>= 4
    header = []
    while size:
        header.append(byte | 0x80)
        byte = size & 0x7f
        size >>= 7
    header.append(byte)
    return bytes(header) + zlib.compress(data)


def create_pack(objects):
    """创建包文件，包含给定给定的sha - 1哈希集合中的所有对象，返回完整包文件的数据字节。
    """
    header = struct.pack('!4sLL', b'PACK', 2, len(objects))
    body = b''.join(encode_pack_object(o) for o in sorted(objects))
    contents = header + body
    sha1 = hashlib.sha1(contents).digest()
    data = contents + sha1
    return data


def push(git_url, username=None, password=None):
    """将主分支推到给定的git repo URL。"""
    if username is None:
        username = os.environ['GIT_USERNAME']
    if password is None:
        password = os.environ['GIT_PASSWORD']
    remote_sha1 = get_remote_master_hash(git_url, username, password)
    local_sha1 = get_local_master_hash()
    missing = find_missing_objects(local_sha1, remote_sha1)
    print('updating remote master from {} to {} ({} object{})'.format(
        remote_sha1 or 'no commits', local_sha1, len(missing),
        '' if len(missing) == 1 else 's'))
    lines = ['{} {} refs/heads/master\x00 report-status'.format(
        remote_sha1 or ('0' * 40), local_sha1).encode()]
    data = build_lines_data(lines) + create_pack(missing)
    url = git_url + '/git-receive-pack'
    response = http_request(url, username, password, data=data)
    lines = extract_lines(response)
    assert len(lines) >= 2, \
        'expected at least 2 lines, got {}'.format(len(lines))
    assert lines[0] == b'unpack ok\n', \
        "expected line 1 b'unpack ok', got: {}".format(lines[0])
    assert lines[1] == b'ok refs/heads/master\n', \
        "expected line 2 b'ok refs/heads/master\n', got: {}".format(lines[1])
    return (remote_sha1, missing)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(dest='command', metavar='command')
    sub_parsers.required = True

    sub_parser = sub_parsers.add_parser('add',
                                        help='add file(s) to index')
    sub_parser.add_argument('paths', nargs='+', metavar='path',
                            help='path(s) of files to add')

    sub_parser = sub_parsers.add_parser('cat-file',
                                        help='display contents of object')
    valid_modes = ['commit', 'tree', 'blob', 'size', 'type', 'pretty']
    sub_parser.add_argument('mode', choices=valid_modes,
                            help='object type (commit, tree, blob) or display mode (size, '
                                 'type, pretty)')
    sub_parser.add_argument('hash_prefix',
                            help='SHA-1 hash (or hash prefix) of object to display')

    sub_parser = sub_parsers.add_parser('commit',
                                        help='commit current state of index to master branch')
    sub_parser.add_argument('-a', '--author',
                            help='commit author in format "A U Thor <author@example.com>" '
                                 '(uses GIT_AUTHOR_NAME and GIT_AUTHOR_EMAIL environment '
                                 'variables by default)')
    sub_parser.add_argument('-m', '--message', required=True,
                            help='text of commit message')

    sub_parser = sub_parsers.add_parser('diff',
                                        help='show diff of files changed (between index and working '
                                             'copy)')

    sub_parser = sub_parsers.add_parser('hash-object',
                                        help='hash contents of given path (and optionally write to '
                                             'object store)')
    sub_parser.add_argument('path',
                            help='path of file to hash')
    sub_parser.add_argument('-t', choices=['commit', 'tree', 'blob'],
                            default='blob', dest='type',
                            help='type of object (default %(default)r)')
    sub_parser.add_argument('-w', action='store_true', dest='write',
                            help='write object to object store (as well as printing hash)')

    sub_parser = sub_parsers.add_parser('init',
                                        help='initialize a new repo')
    sub_parser.add_argument('repo',
                            help='directory name for new repo')

    sub_parser = sub_parsers.add_parser('ls-files',
                                        help='list files in index')
    sub_parser.add_argument('-s', '--stage', action='store_true',
                            help='show object details (mode, hash, and stage number) in '
                                 'addition to path')

    sub_parser = sub_parsers.add_parser('push',
                                        help='push master branch to given git server URL')
    sub_parser.add_argument('git_url',
                            help='URL of git repo, eg: https://github.com/benhoyt/pygit.git')
    sub_parser.add_argument('-p', '--password',
                            help='password to use for authentication (uses GIT_PASSWORD '
                                 'environment variable by default)')
    sub_parser.add_argument('-u', '--username',
                            help='username to use for authentication (uses GIT_USERNAME '
                                 'environment variable by default)')

    sub_parser = sub_parsers.add_parser('status',
                                        help='show status of working copy')

    args = parser.parse_args()
    if args.command == 'add':
        add(args.paths)
    elif args.command == 'cat-file':
        try:
            cat_file(args.mode, args.hash_prefix)
        except ValueError as error:
            print(error, file=sys.stderr)
            sys.exit(1)
    elif args.command == 'commit':
        commit(args.message, author=args.author)
    elif args.command == 'diff':
        diff()
    elif args.command == 'hash-object':
        sha1 = hash_object(read_file(args.path), args.type, write=args.write)
        print(sha1)
    elif args.command == 'init':
        init(args.repo)
    elif args.command == 'ls-files':
        ls_files(details=args.stage)
    elif args.command == 'push':
        push(args.git_url, username=args.username, password=args.password)
    elif args.command == 'status':
        status()
    else:
        assert False, 'unexpected command {!r}'.format(args.command)