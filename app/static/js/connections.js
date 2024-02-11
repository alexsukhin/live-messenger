class Tree {
    constructor() {
        this.root = null;
    }

    addRoot(value) {
        this.root = new TreeNode(value);
        return this.root;
    }

}

class TreeNode {
    constructor(value) {
        this.value = value;
        this.children = [];
    }

    addChild(value) {
        const newNode = new TreeNode(value);
        this.children.push(newNode);
        return newNode;
    }
}

class Queue {
    constructor() {
        this.elements = [];
    }

    enqueue(element) {
        this.elements.push(element)
    }

    dequeue() {
        return this.elements.shift();
    }

    isEmpty() {
        return this.elements.length === 0;
    }
}

export function bfs(root) {

    if (!root) return [];

    const result = [];
    const visited = new Set();
    const queue = new Queue();
    
    for (const child of root.children) {
        queue.enqueue(child)
        visited.add(child.value.userID);
    }

    while (!queue.isEmpty()) {
        const currentNode = queue.dequeue();

        result.push(currentNode.value);

        for (const child of currentNode.children) {
            if (!visited.has(child.value.userID)) {
                visited.add(child.value.userID)
                queue.enqueue(child)
            }
        }
    }

    //This filter function gets filters out the first node and the nodes children
    const filteredResult = result.filter(nodeValue => {

        if (nodeValue.userID === root.value) {
            return false;
        }

        for (const child of root.children) {
            if (nodeValue.userID === child.value.userID) {
                return false;
            }
        }

        return true;
    })


    return filteredResult;
}

export const tree = new Tree()

